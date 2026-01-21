from io import BytesIO

import nba_api.stats.endpoints as nba
import pandas as pd
import requests
from bs4 import BeautifulSoup
from loguru import logger
from nba_api.stats.endpoints import leaguegamefinder
from nba_api.stats.static import players, teams
from PIL import Image

from nbastatpy.standardize import standardize_dataframe
from nbastatpy.utils import Formatter, MeasureTypes, PlayTypes


class Player:
    def __init__(
        self,
        player: str,
        season_year: str | None = None,
        playoffs: bool = False,
        permode: str = "PERGAME",
    ):
        """
        Initializes a Player object.

        Args:
            player (str): The name or ID of the player.
            season_year (str, optional): The season year. Defaults to None.
            playoffs (bool, optional): Whether to retrieve playoff data. Defaults to False.
            permode (str, optional): The per mode for the player's stats. Defaults to "PERGAME".
        """
        self.permode = PlayTypes.PERMODE[
            permode.replace("_", "").replace("-", "").upper()
        ]
        self.name_meta = players.find_player_by_id(player)
        if self.name_meta:
            self.name_meta = [self.name_meta]
        else:
            self.name_meta = players.find_players_by_full_name(player)

        if not self.name_meta:
            raise ValueError(f"{player} not found")
        if len(self.name_meta) > 1:
            logger.warning(
                f"Multiple players returned. Using: {self.name_meta[0]['full_name']}"
            )
        self.id = self.name_meta[0]["id"]
        self.name = self.name_meta[0]["full_name"]
        self.first_name = self.name_meta[0]["first_name"]
        self.last_name = self.name_meta[0]["last_name"]
        self.is_active = self.name_meta[0]["is_active"]

        if season_year:
            self.season_year = season_year
        else:
            self.season_year = Formatter.get_current_season_year()
        self.season = Formatter.format_season(self.season_year)
        self.season_type = "Regular Season"
        if playoffs:
            self.season_type = "Playoffs"

    def get_common_info(self, standardize: bool = False) -> pd.DataFrame:
        """Gets common info like height, weight, draft_year, etc. and sets as class attr

        Args:
            standardize: Whether to apply data standardization

        Returns:
            pd.DataFrame: A DataFrame containing the common information of the player.
        """
        df = nba.CommonPlayerInfo(self.id).get_data_frames()[0]

        if standardize:
            df = standardize_dataframe(df, data_type="player")

        self.common_info = df.iloc[0].to_dict()

        for attr_name, value in self.common_info.items():
            setattr(self, attr_name.lower(), self.common_info.get(attr_name, None))

        return df

    def get_salary(self, standardize: bool = False) -> pd.DataFrame:
        """
        Retrieves the salary information for a player from hoopshype.com.

        Args:
            standardize: Whether to apply data standardization

        Returns:
            pd.DataFrame: A DataFrame containing the salary information for the player.
        """
        salary_url = f"https://hoopshype.com/player/{self.first_name}-{self.last_name}/salary/".lower()
        result = requests.get(salary_url)
        soup = BeautifulSoup(result.content, features="html.parser")
        tables = soup.find_all("table")
        if len(tables) > 1:
            # Get the table rows
            rows = [
                [cell.text.strip() for cell in row.find_all("td")]
                for row in tables[2].find_all("tr")
            ]

            rows2 = [
                [cell.text.strip() for cell in row.find_all("td")]
                for row in tables[3].find_all("tr")
            ]

            # Define columns - use first row if non-empty, otherwise use default
            if rows[0]:
                cols = rows[0]
            else:
                cols = ["Season", "Team", "Salary"]

            projected = pd.DataFrame(rows[1:], columns=cols)
            projected["Team"] = "Projected"
            projected["Salary_Type"] = "Projected"

            historical = pd.DataFrame(rows2[1:], columns=cols)
            historical["Salary_Type"] = "Historical"

            self.salary_df = pd.concat([projected, historical])

        else:
            # Get the table rows
            rows = [
                [cell.text.strip() for cell in row.find_all("td")]
                for row in tables[0].find_all("tr")
            ]
            self.salary_df = pd.DataFrame(rows[1:], columns=rows[0])

        if standardize:
            # Make all columns lowercase
            self.salary_df.columns = [col.lower() for col in self.salary_df.columns]

            # Filter out rows where season is 'Total'
            if "season" in self.salary_df.columns:
                self.salary_df = self.salary_df[
                    self.salary_df["season"].str.lower() != "total"
                ]

                # Convert season column to YYYYYYYY format
                self.salary_df["season"] = self.salary_df["season"].apply(
                    lambda x: Formatter.format_season_id(x) if pd.notna(x) else None
                )

            # Remove repeated team name suffix
            if "team" in self.salary_df.columns:

                def remove_duplicate_suffix(team_name):
                    if pd.isna(team_name) or team_name == "":
                        return team_name
                    team_str = str(team_name).strip()
                    words = team_str.split()
                    if len(words) >= 2:
                        # The last word will be the duplicated part (e.g., "LakersLakers")
                        last_word = words[-1]
                        # Check if it's even length and first half equals second half
                        if len(last_word) % 2 == 0:
                            mid = len(last_word) // 2
                            if last_word[:mid] == last_word[mid:]:
                                # Replace the duplicated word with the single version
                                words[-1] = last_word[:mid]
                                return " ".join(words)
                    return team_str

                self.salary_df["team"] = self.salary_df["team"].apply(
                    remove_duplicate_suffix
                )

            # Clean and convert salary column to integer
            if "salary" in self.salary_df.columns:

                def clean_salary(salary_value):
                    if pd.isna(salary_value) or salary_value == "":
                        return None
                    # Remove all non-numeric characters except digits
                    import re

                    numeric_only = re.sub(r"[^\d]", "", str(salary_value))
                    if numeric_only:
                        return int(numeric_only)
                    return None

                self.salary_df["salary"] = self.salary_df["salary"].apply(clean_salary)

        return self.salary_df

    def get_headshot(self):
        """
        Retrieves the headshot image of the player.

        Returns:
            PIL.Image.Image: The headshot image of the player.
        """
        pic_url = f"https://cdn.nba.com/headshots/nba/latest/1040x760/{self.id}.png"
        pic = requests.get(pic_url)
        self.headshot = Image.open(BytesIO(pic.content))
        return self.headshot

    def get_season_career_totals(self, standardize: bool = False) -> pd.DataFrame:
        """Gets seasons and career data

        Args:
            standardize: Whether to apply data standardization

        Returns:
            pd.DataFrame: 2 dataframes, season totals and career
        """
        df_list = nba.PlayerCareerStats(player_id=self.id).get_data_frames()

        if standardize:
            self.career_totals = standardize_dataframe(df_list[1], data_type="player")
            self.season_totals = standardize_dataframe(df_list[0], data_type="player")
        else:
            self.career_totals = df_list[1]
            self.season_totals = df_list[0]

        return self.season_totals, self.career_totals

    def get_career_stats_by_year(
        self,
        measure_type: str = "Base",
        per_mode: str | None = None,
        standardize: bool = False,
    ) -> pd.DataFrame:
        """Get career statistics broken down by season with flexible stat types and per-modes.

        Unlike get_season_career_totals() which only supports basic stats with limited
        per-modes, this method supports advanced statistics and all per-mode options
        including Per100Possessions.

        Args:
            measure_type: Type of statistics to include:
                - "Base": Traditional stats (PTS, REB, AST, etc.)
                - "Advanced": Advanced metrics (TS_PCT, OFF_RATING, DEF_RATING, etc.)
                - "Misc": Miscellaneous stats
                - "Scoring": Scoring breakdown stats
                - "Usage": Usage statistics
            per_mode: How to calculate statistics:
                - "PerGame": Per game averages (default)
                - "Per36": Per 36 minutes
                - "Per100Possessions": Per 100 possessions
                - "Totals": Raw totals
                If None, uses instance's permode setting.
            standardize: Whether to apply data standardization.

        Returns:
            pd.DataFrame: Season-by-season career statistics.
        """
        # Normalize measure_type
        measure_key = (
            measure_type.replace("_", "").replace("-", "").replace(" ", "").upper()
        )
        if measure_key not in MeasureTypes.TYPES:
            valid = sorted(set(MeasureTypes.TYPES.values()))
            raise ValueError(f"Invalid measure_type '{measure_type}'. Valid: {valid}")
        normalized_measure = MeasureTypes.TYPES[measure_key]

        # Use provided per_mode or fall back to instance setting
        actual_permode = per_mode if per_mode else self.permode

        df = nba.PlayerDashboardByYearOverYear(
            player_id=self.id,
            measure_type_detailed=normalized_measure,
            per_mode_detailed=actual_permode,
            season_type_playoffs=self.season_type,
        ).get_data_frames()[1]  # Index 1 = ByYearPlayerDashboard

        if standardize:
            df = standardize_dataframe(df, data_type="player")

        self.career_stats_by_year = df
        return self.career_stats_by_year

    def get_splits(self) -> pd.DataFrame:
        """Gets all splits for a given season"""

        self.splits_data = pd.concat(
            nba.PlayerDashboardByGeneralSplits(
                self.id,
                season=self.season,
                season_type_playoffs=self.season_type,
                per_mode_detailed=self.permode,
            ).get_data_frames()
        )

        return self.splits_data

    def get_game_splits(self) -> pd.DataFrame:
        """Gets splits for the game (halftime, quarter, etc.)

        Returns:
            pd.DataFrame: dataframe with all game splits for a season
        """

        self.game_splits = pd.concat(
            nba.PlayerDashboardByGameSplits(
                self.id,
                season=self.season,
                season_type_playoffs=self.season_type,
                per_mode_detailed=self.permode,
            ).get_data_frames()
        )
        return self.game_splits

    def get_shooting_splits(self) -> pd.DataFrame:
        self.shooting_splits = pd.concat(
            nba.PlayerDashboardByShootingSplits(
                self.id,
                season=self.season,
                season_type_playoffs=self.season_type,
                per_mode_detailed=self.permode,
            ).get_data_frames()
        )
        return self.shooting_splits

    def get_combine_stats(self) -> pd.DataFrame:
        """Gets draft combine data for the player's draft year"""
        if not hasattr(
            self, "draft_year"
        ):  # Check if we know the player's draft year yet
            self.get_common_info()

        self.combine_stats = nba.DraftCombineStats(
            season_all_time=self.draft_year
        ).get_data_frames()[0]

        self.combine_nonstationary_shooting = nba.DraftCombineNonStationaryShooting(
            season_year=self.draft_year
        ).get_data_frames()[0]

        self.combine_spot_shooting = nba.DraftCombineSpotShooting(
            season_year=self.draft_year
        ).get_data_frames()[0]

        return [
            self.combine_stats,
            self.combine_nonstationary_shooting,
            self.combine_spot_shooting,
        ]

    def get_awards(self) -> pd.DataFrame:
        """Gets any awards won by the player.

        Returns:
            pd.DataFrame: A DataFrame containing the player's awards.
        """
        self.awards = nba.PlayerAwards(self.id).get_data_frames()[0]
        return self.awards

    def get_games_boxscore(self, standardize: bool = False) -> pd.DataFrame:
        """
        Retrieves the boxscore data for the games played by the player.

        Args:
            standardize: Whether to apply data standardization

        Returns:
            pd.DataFrame: The boxscore data for the player's games.
        """
        df = leaguegamefinder.LeagueGameFinder(
            player_id_nullable=self.id,
            season_nullable=self.season,
            season_type_nullable=self.season_type,
        ).get_data_frames()[0]

        if standardize:
            df = standardize_dataframe(
                df,
                data_type="player",
                season=self.season,
                playoffs=(self.season_type == "Playoffs"),
            )

        self.games_boxscore = df
        return self.games_boxscore

    def get_game_logs(
        self,
        last_n_games: int | None = None,
        measure_type: str = "Base",
        per_mode: str | None = None,
        standardize: bool = False,
    ) -> pd.DataFrame:
        """
        Retrieves detailed game logs for the player with configurable stat types.

        Args:
            last_n_games: Number of most recent games to retrieve.
                          If None, returns all games for the season.
            measure_type: Type of statistics to include:
                          - "Base": Traditional stats (PTS, REB, AST, etc.)
                          - "Advanced": Advanced metrics (OFF_RATING, DEF_RATING, TS_PCT, etc.)
                          - "Misc": Miscellaneous stats
                          - "Scoring": Scoring breakdown stats
                          - "Usage": Usage statistics
            per_mode: How to calculate statistics:
                      - "PerGame": Per game averages (default)
                      - "Per36": Per 36 minutes
                      - "Per100Possessions": Per 100 possessions
                      - "PerMinute": Per minute
                      - "Totals": Raw totals
                      If None, uses instance's permode setting.
            standardize: Whether to apply data standardization.

        Returns:
            pd.DataFrame: Game logs with the requested statistics.
                          When standardize=True, column names are lowercase.
                          When standardize=False, column names are uppercase (as returned by API).
        """
        # Validate last_n_games parameter
        if last_n_games is not None and (last_n_games < 1 or last_n_games > 82):
            raise ValueError(
                f"last_n_games must be between 1 and 82, got {last_n_games}"
            )

        # Normalize measure_type
        measure_key = (
            measure_type.replace("_", "").replace("-", "").replace(" ", "").upper()
        )
        if measure_key not in MeasureTypes.TYPES:
            valid = sorted(set(MeasureTypes.TYPES.values()))
            raise ValueError(f"Invalid measure_type '{measure_type}'. Valid: {valid}")
        normalized_measure = MeasureTypes.TYPES[measure_key]

        # Use provided per_mode or fall back to instance setting
        actual_permode = per_mode if per_mode else self.permode

        df = nba.PlayerGameLogs(
            player_id_nullable=self.id,
            season_nullable=self.season,
            season_type_nullable=self.season_type,
            measure_type_player_game_logs_nullable=normalized_measure,
            per_mode_simple_nullable=actual_permode,
            last_n_games_nullable=last_n_games,
        ).get_data_frames()[0]

        if standardize:
            df = standardize_dataframe(
                df,
                data_type="player",
                season=self.season,
                playoffs=(self.season_type == "Playoffs"),
            )

        self.game_logs = df
        return self.game_logs

    def get_matchups(self, defense: bool = False) -> pd.DataFrame:
        """
        Retrieves the matchups data for the player.

        Args:
            defense (bool, optional): If True, retrieves the defensive matchups data.
                If False, retrieves the offensive matchups data. Defaults to False.

        Returns:
            pd.DataFrame: The matchups data for the player.
        """
        if defense:
            self.matchups = nba.LeagueSeasonMatchups(
                def_player_id_nullable=self.id,
                season=self.season,
                season_type_playoffs=self.season_type,
                per_mode_simple=self.permode,
            ).get_data_frames()[0]
        else:
            self.matchups = nba.LeagueSeasonMatchups(
                off_player_id_nullable=self.id,
                season=self.season,
                season_type_playoffs=self.season_type,
                per_mode_simple=self.permode,
            ).get_data_frames()[0]
        return self.matchups

    def get_clutch(self) -> pd.DataFrame:
        """Gets clutch data for multiple clutch segments

        Returns:
            pd.DataFrame: dataframe with a given year of clutch segments
        """
        self.clutch = pd.concat(
            nba.PlayerDashboardByClutch(
                player_id=self.id,
                season=self.season,
                season_type_playoffs=self.season_type,
                per_mode_detailed=self.permode,
            ).get_data_frames()
        )
        return self.clutch

    def _get_player_teams_for_season(self) -> list[int]:
        """Get the team ID(s) for the player in the current season.

        Handles mid-season trades by returning multiple team IDs.
        Fetches season totals if not already cached.

        Returns:
            list[int]: List of team IDs the player played for this season.
        """
        if not hasattr(self, "season_totals"):
            logger.info("Getting Teams")
            self.get_season_career_totals()

        teams_df = self.season_totals.copy()
        team_ids = teams_df[
            (teams_df["SEASON_ID"] == self.season) & (teams_df["TEAM_ID"] != 0)
        ]["TEAM_ID"].tolist()

        return team_ids

    def get_pt_pass(self) -> pd.DataFrame:
        """
        Retrieves the passing statistics for the player.

        Returns:
            pd.DataFrame: A DataFrame containing the passing statistics for the player.
        """
        teams = self._get_player_teams_for_season()

        if len(teams) > 1:
            self.pt_pass = []
            for team in teams:
                self.pt_pass.append(
                    pd.concat(
                        nba.PlayerDashPtPass(
                            player_id=self.id,
                            team_id=team,
                            season=self.season,
                            season_type_all_star=self.season_type,
                            per_mode_simple=self.permode,
                        ).get_data_frames()
                    )
                )

            self.pt_pass = pd.concat(self.pt_pass)

        else:
            self.pt_pass = pd.concat(
                nba.PlayerDashPtPass(
                    player_id=self.id,
                    team_id=teams[0],
                    season=self.season,
                    season_type_all_star=self.season_type,
                    per_mode_simple=self.permode,
                ).get_data_frames()
            )

        group_cols = ["PASS_TO", "PASS_FROM"]
        self.pt_pass["GROUP_SET"] = self.pt_pass[group_cols].apply(
            Formatter.combine_strings, axis=1
        )
        self.pt_pass = self.pt_pass.drop(columns=group_cols)

        return self.pt_pass

    def get_pt_reb(self) -> pd.DataFrame:
        """
        Retrieves the rebounds data for the player.

        Returns:
            pd.DataFrame: A DataFrame containing the rebounds data.
        """
        teams = self._get_player_teams_for_season()

        if len(teams) > 1:
            self.pt_reb = []
            for team in teams:
                self.pt_reb.append(
                    pd.concat(
                        nba.PlayerDashPtReb(
                            player_id=self.id,
                            team_id=team,
                            season=self.season,
                            season_type_all_star=self.season_type,
                            per_mode_simple=self.permode,
                        ).get_data_frames()
                    )
                )

            self.pt_reb = pd.concat(self.pt_reb)

        else:
            self.pt_reb = pd.concat(
                nba.PlayerDashPtReb(
                    player_id=self.id,
                    team_id=teams[0],
                    season=self.season,
                    season_type_all_star=self.season_type,
                    per_mode_simple=self.permode,
                ).get_data_frames()
            )

        group_cols = [
            "OVERALL",
            "SHOT_TYPE_RANGE",
            "REB_NUM_CONTESTING_RANGE",
            "SHOT_DIST_RANGE",
            "REB_DIST_RANGE",
        ]
        self.pt_reb["GROUP_SET"] = self.pt_reb[group_cols].apply(
            Formatter.combine_strings, axis=1
        )
        self.pt_reb = self.pt_reb.drop(columns=group_cols)

        return self.pt_reb

    def get_defense_against_team(self, opposing_team: str) -> pd.DataFrame:
        """
        Retrieves the defensive statistics of the player against a specific team.

        Args:
            opposing_team (str): The abbreviation of the opposing team.

        Returns:
            pd.DataFrame: A DataFrame containing the defensive statistics of the player against the specified team.
        """
        opp_tm_id = teams.find_team_by_abbreviation(opposing_team)["id"]

        self.defense_against_team = nba.PlayerDashPtShotDefend(
            player_id=self.id,
            team_id=opp_tm_id,
            season=self.season,
            season_type_all_star=self.season_type,
            per_mode_simple=self.permode,
        ).get_data_frames()[0]
        return self.defense_against_team

    def get_pt_shots(self) -> pd.DataFrame:
        """
        Retrieves the shots data for the player.

        Returns:
            pd.DataFrame: The shots data for the player.
        """
        teams = self._get_player_teams_for_season()

        if len(teams) > 1:
            self.pt_shots = []
            for team in teams:
                self.pt_shots.append(
                    pd.concat(
                        nba.PlayerDashPtShots(
                            player_id=self.id,
                            team_id=team,
                            season=self.season,
                            season_type_all_star=self.season_type,
                            per_mode_simple=self.permode,
                        ).get_data_frames()
                    )
                )

            self.pt_shots = pd.concat(self.pt_shots)

        else:
            self.pt_shots = pd.concat(
                nba.PlayerDashPtShots(
                    player_id=self.id,
                    team_id=teams[0],
                    season=self.season,
                    season_type_all_star=self.season_type,
                    per_mode_simple=self.permode,
                ).get_data_frames()
            )

        group_cols = [
            "SHOT_TYPE",
            "SHOT_CLOCK_RANGE",
            "DRIBBLE_RANGE",
            "CLOSE_DEF_DIST_RANGE",
            "TOUCH_TIME_RANGE",
        ]
        self.pt_shots["GROUP_SET"] = self.pt_shots[group_cols].apply(
            Formatter.combine_strings, axis=1
        )
        self.pt_shots = self.pt_shots.drop(columns=group_cols)

        return self.pt_shots

    def get_shot_chart(self) -> pd.DataFrame:
        """
        Retrieves the shot chart data for the player.

        Returns:
            pd.DataFrame: The shot chart data for the player.
        """
        teams = self._get_player_teams_for_season()

        if len(teams) > 1:
            self.shot_chart = []
            for team in teams:
                self.shot_chart.append(
                    nba.ShotChartDetail(
                        player_id=self.id,
                        team_id=team,
                        season_nullable=self.season,
                        season_type_all_star=self.season_type,
                    ).get_data_frames()[0]
                )

            self.shot_chart = pd.concat(self.shot_chart)

        else:
            self.shot_chart = nba.ShotChartDetail(
                player_id=self.id,
                team_id=teams[0],
                season_nullable=self.season,
                season_type_all_star=self.season_type,
            ).get_data_frames()[0]

        return self.shot_chart


if __name__ == "__main__":
    player_name = "giannis"
    player_seas = "2020"
    player = Player(player_name, player_seas)
    print(player.get_salary())
