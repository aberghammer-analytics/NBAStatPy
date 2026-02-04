import nba_api.stats.endpoints as nba
import pandas as pd
import requests
from nba_api.stats.static import teams
from rich.progress import track

from nbastatpy.config import REQUEST_TIMEOUT, LeagueID
from nbastatpy.standardize import standardize_dataframe
from nbastatpy.utils import Formatter, PlayTypes, Validators, rate_limiter


class Team:
    def __init__(
        self,
        team_abbreviation: str,
        season_year: str | None = None,
        playoffs: bool = False,
        permode: str = "PerGame",
    ):
        """
        Initializes a Team object.

        Automatically detects whether the team is in the NBA or WNBA based on
        the team abbreviation. NBA is checked first, then WNBA.

        Parameters:
        - team_abbreviation (str): The abbreviation of the NBA or WNBA team.
        - season_year (str, optional): The season year. If not provided, the current season year will be used.
        - playoffs (bool, optional): Specifies whether the team's statistics are for playoffs. Default is False.
        - permode (str, optional): The mode for the team's statistics. Default is "PerGame".

        Attributes:
        - permode (str): The formatted permode for the team's statistics.
        - season_year (str): The season year.
        - info (dict): The information about the team.
        - season (str): The formatted season.
        - season_type (str): The type of season (Regular Season or Playoffs).
        - league (str): The league the team belongs to ("NBA" or "WNBA").
        - league_id (str): The league ID for API calls ("00" or "10").

        Raises:
            ValueError: If the team abbreviation is not found in either NBA or WNBA.

        Examples:
            >>> team = Team("MIL")  # Auto-detects NBA (Milwaukee Bucks)
            >>> team.league
            'NBA'
            >>> team = Team("LVA")  # Auto-detects WNBA (Las Vegas Aces)
            >>> team.league
            'WNBA'
        """
        self.permode = PlayTypes.PERMODE[
            permode.replace("_", "").replace("-", "").upper()
        ]

        # Auto-detect league from team abbreviation
        detected_league = Validators.detect_team_league(team_abbreviation)
        if detected_league is None:
            raise ValueError(
                f"Team abbreviation '{team_abbreviation}' not found in NBA or WNBA"
            )
        self.league = detected_league

        # Look up team info in the appropriate league
        if self.league == "WNBA":
            self.info = teams.find_wnba_team_by_abbreviation(team_abbreviation)
        else:
            self.info = teams.find_team_by_abbreviation(team_abbreviation)

        if not self.info:
            raise ValueError(
                f"Team abbreviation '{team_abbreviation}' not found in {self.league}"
            )

        # Set league ID for API calls
        self.league_id = LeagueID.from_string(self.league)

        if season_year:
            self.season_year = Formatter.normalize_season_year(season_year)
        else:
            self.season_year = Formatter.get_current_season_year(self.league)

        # Format season based on league (WNBA uses single year format)
        self.season = Formatter.format_season_for_league(self.season_year, self.league)
        self.season_type = "Regular Season"
        if playoffs:
            self.season_type = "Playoffs"

        for attr_name, value in self.info.items():
            setattr(self, attr_name.lower(), self.info.get(attr_name, None))

    def get_logo(self):
        """
        Retrieves and returns the logo of the NBA or WNBA team in svg format.

        Note: WNBA team logos may not be available from the same CDN.

        Returns:
            bytes: The logo content of the team.
        """
        if self.league == "WNBA":
            # WNBA logos use a different URL pattern
            pic_url = f"https://cdn.wnba.com/logos/wnba/{self.id}/primary/L/logo.svg"
        else:
            pic_url = f"https://cdn.nba.com/logos/nba/{self.id}/primary/L/logo.svg"
        pic = requests.get(pic_url, timeout=REQUEST_TIMEOUT)
        self.logo = pic.content
        return self.logo

    def get_roster(self, standardize: bool = False) -> list[pd.DataFrame]:
        """
        Retrieves the roster of the team for the specified season.

        Args:
            standardize: Whether to apply data standardization

        Returns:
            List[pd.DataFrame]: A list of pandas DataFrames containing the roster data.
        """
        dfs = nba.CommonTeamRoster(
            self.id,
            season=self.season,
            league_id_nullable=self.league_id,
        ).get_data_frames()

        if standardize:
            dfs = [
                standardize_dataframe(
                    df,
                    data_type="team",
                    season=self.season,
                    playoffs=(self.season_type == "Playoffs"),
                )
                for df in dfs
            ]

        self.roster = dfs
        return self.roster

    def get_year_by_year(self) -> pd.DataFrame:
        """
        Retrieves the year-by-year statistics for the team.

        Returns:
            pd.DataFrame: The year-by-year statistics for the team.
        """
        self.year_by_year = nba.TeamYearByYearStats(
            team_id=self.id,
            per_mode_simple=self.permode,
            league_id=self.league_id,
        ).get_data_frames()[0]
        return self.year_by_year

    def get_general_splits(self) -> pd.DataFrame:
        """
        Retrieves the general splits data for the team.

        Returns:
            pd.DataFrame: The general splits data for the team.
        """
        drop_cols = [
            "TEAM_GAME_LOCATION",
            "GAME_RESULT",
            "SEASON_MONTH_NAME",
            "SEASON_SEGMENT",
            "TEAM_DAYS_REST_RANGE",
        ]
        self.general_splits = pd.concat(
            nba.TeamDashboardByGeneralSplits(
                team_id=self.id,
                season=self.season,
                season_type_all_star=self.season_type,
                per_mode_detailed=self.permode,
                league_id_nullable=self.league_id,
            ).get_data_frames()
        ).drop(columns=drop_cols, errors="ignore")
        return self.general_splits

    def get_shooting_splits(self) -> pd.DataFrame:
        """
        Retrieves shooting splits data for the team.

        Returns:
            pd.DataFrame: The shooting splits data for the team.
        """
        self.shooting_splits = pd.concat(
            nba.TeamDashboardByShootingSplits(
                team_id=self.id,
                season=self.season,
                season_type_all_star=self.season_type,
                per_mode_detailed=self.permode,
                league_id_nullable=self.league_id,
            ).get_data_frames()
        )
        return self.shooting_splits

    def get_leaders(self) -> pd.DataFrame:
        """
        Retrieves the franchise leaders data for the team.

        Returns:
            pd.DataFrame: The franchise leaders data for the team.
        """
        self.leaders = nba.FranchiseLeaders(
            team_id=self.id, league_id_nullable=self.league_id
        ).get_data_frames()[0]
        return self.leaders

    def get_franchise_players(self) -> pd.DataFrame:
        """
        Retrieves the franchise players for the team.

        Returns:
            pd.DataFrame: A DataFrame containing the franchise players' data.
        """
        self.franchise_players = nba.FranchisePlayers(
            team_id=self.id, league_id=self.league_id
        ).get_data_frames()[0]
        return self.franchise_players

    def get_season_lineups(self) -> pd.DataFrame:
        """
        Retrieves the season lineups for the team.

        Returns:
            pd.DataFrame: A DataFrame containing the season lineups data.
        """
        self.season_lineups = nba.LeagueDashLineups(
            team_id_nullable=self.id,
            season=self.season,
            season_type_all_star=self.season_type,
            per_mode_detailed=self.permode,
            league_id_nullable=self.league_id,
        ).get_data_frames()[0]
        self.season_lineups["season"] = self.season
        self.season_lineups["season_type"] = self.season_type

        return self.season_lineups

    def get_opponent_shooting(self) -> pd.DataFrame:
        """
        Retrieves the opponent shooting statistics for the team.

        Returns:
            pd.DataFrame: DataFrame containing the opponent shooting statistics.
        """
        self.opponent_shooting = nba.LeagueDashOppPtShot(
            team_id_nullable=self.id,
            season=self.season,
            season_type_all_star=self.season_type,
            per_mode_simple=self.permode,
            league_id=self.league_id,
        ).get_data_frames()[0]
        self.opponent_shooting["season"] = self.season
        self.opponent_shooting["season_type"] = self.season_type

        return self.opponent_shooting

    def get_player_clutch(self) -> pd.DataFrame:
        """
        Retrieves the clutch statistics for the players of the team.

        Returns:
            pd.DataFrame: A DataFrame containing the clutch statistics for the players of the team.
        """
        self.player_clutch = nba.LeagueDashPlayerClutch(
            team_id_nullable=self.id,
            season=self.season,
            season_type_all_star=self.season_type,
            per_mode_detailed=self.permode,
            league_id_nullable=self.league_id,
        ).get_data_frames()[0]
        self.player_clutch["season"] = self.season
        self.player_clutch["season_type"] = self.season_type

        return self.player_clutch

    def get_player_shots(self) -> pd.DataFrame:
        """
        Retrieves the player shots data for the team.

        Returns:
            pd.DataFrame: The player shots data for the team.
        """
        self.player_shots = nba.LeagueDashPlayerPtShot(
            team_id_nullable=self.id,
            season=self.season,
            season_type_all_star=self.season_type,
            per_mode_simple=self.permode,
            league_id=self.league_id,
        ).get_data_frames()[0]
        self.player_shots["season"] = self.season
        self.player_shots["season_type"] = self.season_type

        return self.player_shots

    def get_player_shot_locations(self) -> pd.DataFrame:
        """
        Retrieves the shot locations data for the players of the team.

        Returns:
            pd.DataFrame: A DataFrame containing the shot locations data for the players.
        """
        self.player_shot_locations = nba.LeagueDashPlayerShotLocations(
            team_id_nullable=self.id,
            season=self.season,
            season_type_all_star=self.season_type,
            per_mode_detailed=self.permode,
            league_id_nullable=self.league_id,
        ).get_data_frames()[0]
        self.player_shot_locations["season"] = self.season
        self.player_shot_locations["season_type"] = self.season_type

        return self.player_shot_locations

    def get_player_stats(self, standardize: bool = False) -> pd.DataFrame:
        """
        Retrieves the player statistics for the team.

        Args:
            standardize: Whether to apply data standardization

        Returns:
            pd.DataFrame: A DataFrame containing the player statistics.
        """
        df = nba.LeagueDashPlayerStats(
            team_id_nullable=self.id,
            season=self.season,
            season_type_all_star=self.season_type,
            per_mode_detailed=self.permode,
            league_id_nullable=self.league_id,
        ).get_data_frames()[0]

        df["season"] = self.season
        df["season_type"] = self.season_type

        if standardize:
            df = standardize_dataframe(
                df,
                data_type="team",
                season=self.season,
                playoffs=(self.season_type == "Playoffs"),
            )

        self.player_stats = df
        return self.player_stats

    def get_player_point_defend(self) -> pd.DataFrame:
        """
        Retrieves the player point defense data for the team.

        Returns:
            pd.DataFrame: The player point defense data for the team.
        """
        self.player_point_defend = nba.LeagueDashPtDefend(
            team_id_nullable=self.id,
            season=self.season,
            season_type_all_star=self.season_type,
            per_mode_simple=self.permode,
            league_id=self.league_id,
        ).get_data_frames()[0]
        self.player_point_defend["season"] = self.season
        self.player_point_defend["season_type"] = self.season_type

        return self.player_point_defend

    def get_player_hustle(self) -> pd.DataFrame:
        """
        Retrieves the hustle stats for the players of the team.

        Returns:
            pd.DataFrame: A DataFrame containing the hustle stats for the players.
        """
        self.player_hustle = nba.LeagueHustleStatsPlayer(
            team_id_nullable=self.id,
            season=self.season,
            season_type_all_star=self.season_type,
            league_id_nullable=self.league_id,
        ).get_data_frames()[0]
        self.player_hustle["season"] = self.season
        self.player_hustle["season_type"] = self.season_type

        return self.player_hustle

    def get_lineup_details(self) -> pd.DataFrame:
        """
        Retrieves the lineup details for the team.

        Returns:
            pd.DataFrame: The lineup details for the team.
        """
        self.lineup_details = nba.LeagueLineupViz(
            team_id_nullable=self.id,
            season=self.season,
            season_type_all_star=self.season_type,
            minutes_min=1,
            per_mode_detailed=self.permode,
            league_id_nullable=self.league_id,
        ).get_data_frames()[0]
        self.lineup_details["season"] = self.season
        self.lineup_details["season_type"] = self.season_type

        return self.lineup_details

    def get_player_on_details(self) -> pd.DataFrame:
        """
        Retrieves the player on-court details for the team.

        Returns:
            pd.DataFrame: A DataFrame containing the player on-court details.
        """
        self.player_on_details = nba.LeaguePlayerOnDetails(
            team_id=self.id,
            season=self.season,
            season_type_all_star=self.season_type,
            per_mode_detailed=self.permode,
            league_id_nullable=self.league_id,
        ).get_data_frames()[0]
        self.player_on_details["season"] = self.season
        self.player_on_details["season_type"] = self.season_type

        return self.player_on_details

    def get_player_matchups(self, defense=False) -> pd.DataFrame:
        """
        Retrieves player matchups for the team.

        Args:
            defense (bool, optional): If True, retrieves defensive matchups. If False, retrieves offensive matchups. Defaults to False.

        Returns:
            pd.DataFrame: DataFrame containing player matchups for the team.
        """
        if defense:
            self.player_matchups = nba.LeagueSeasonMatchups(
                def_team_id_nullable=self.id,
                season=self.season,
                season_type_playoffs=self.season_type,
                per_mode_simple=self.permode,
                league_id=self.league_id,
            ).get_data_frames()[0]
        else:
            self.player_matchups = nba.LeagueSeasonMatchups(
                off_team_id_nullable=self.id,
                season=self.season,
                season_type_playoffs=self.season_type,
                per_mode_simple=self.permode,
                league_id=self.league_id,
            ).get_data_frames()[0]

        self.player_matchups["season"] = self.season
        self.player_matchups["season_type"] = self.season_type

        return self.player_matchups

    def get_player_passes(self) -> pd.DataFrame:
        """
        Retrieves the player passes data for the team.

        Returns:
            pd.DataFrame: The player passes data for the team.
        """
        self.player_passes = pd.concat(
            nba.TeamDashPtPass(
                team_id=self.id,
                season=self.season,
                season_type_all_star=self.season_type,
                per_mode_simple=self.permode,
                league_id=self.league_id,
            ).get_data_frames()
        )

        group_cols = ["PASS_FROM", "PASS_TO"]
        self.player_passes["GROUP_SET"] = self.player_passes[group_cols].apply(
            Formatter.combine_strings, axis=1
        )
        self.player_passes = self.player_passes.drop(columns=group_cols)
        return self.player_passes.reset_index(drop=True)

    def get_player_onoff(self) -> pd.DataFrame:
        """
        Retrieves the on-off court details for the players of the team.

        Returns:
            pd.DataFrame: A DataFrame containing the on-off court details for the players.
        """
        self.player_onoff = pd.concat(
            nba.TeamPlayerOnOffDetails(
                team_id=self.id,
                season=self.season,
                season_type_all_star=self.season_type,
                per_mode_detailed=self.permode,
                league_id_nullable=self.league_id,
            ).get_data_frames()[1:]
        )
        return self.player_onoff.reset_index(drop=True)

    def get_game_log(
        self,
        last_n_games: int | None = None,
        include_opponent_stats: bool = False,
        include_advanced_stats: bool = False,
        standardize: bool = False,
    ) -> pd.DataFrame:
        """
        Retrieves the game log for the team with optional opponent and advanced statistics.

        Args:
            last_n_games: Number of most recent games to retrieve. If None, returns all games.
            include_opponent_stats: If True, includes opponent stats with OPP_ prefix.
            include_advanced_stats: If True, includes advanced stats (ratings, pace, four factors).
                Note: This makes additional API calls per game and may be slower.
            standardize: Whether to apply data standardization.

        Returns:
            pd.DataFrame: Game log with team stats, and optionally opponent/advanced stats.
        """
        # Get team's game log
        df = nba.TeamGameLog(
            team_id=self.id,
            season=self.season,
            season_type_all_star=self.season_type,
            league_id_nullable=self.league_id,
        ).get_data_frames()[0]

        # Filter to last n games if specified
        if last_n_games is not None:
            df = df.head(last_n_games)

        # Include opponent stats if requested
        if include_opponent_stats:
            df = self._add_opponent_stats(df)

        # Include advanced stats if requested
        if include_advanced_stats:
            df = self._add_advanced_stats(df)

        if standardize:
            df = standardize_dataframe(
                df,
                data_type="team",
                season=self.season,
                playoffs=(self.season_type == "Playoffs"),
            )

        self.game_log = df
        return self.game_log

    def _add_opponent_stats(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Adds opponent statistics to the game log DataFrame.

        Args:
            df: Game log DataFrame with team stats.

        Returns:
            pd.DataFrame: Game log with opponent stats merged (OPP_ prefix).
        """
        # Get all team game logs for the season
        all_games = nba.LeagueGameLog(
            season=self.season,
            season_type_all_star=self.season_type,
            player_or_team_abbreviation="T",
            league_id=self.league_id,
        ).get_data_frames()[0]

        # Columns to include as opponent stats (exclude metadata columns)
        stat_cols = [
            "FGM",
            "FGA",
            "FG_PCT",
            "FG3M",
            "FG3A",
            "FG3_PCT",
            "FTM",
            "FTA",
            "FT_PCT",
            "OREB",
            "DREB",
            "REB",
            "AST",
            "STL",
            "BLK",
            "TOV",
            "PF",
            "PTS",
            "PLUS_MINUS",
        ]

        # Get opponent rows for each game
        opponent_stats_list = []
        for game_id in df["Game_ID"]:
            game_rows = all_games[all_games["GAME_ID"] == game_id]
            opponent_row = game_rows[game_rows["TEAM_ID"] != self.id]
            if not opponent_row.empty:
                opp_data = {"Game_ID": game_id}
                for col in stat_cols:
                    if col in opponent_row.columns:
                        opp_data[f"OPP_{col}"] = opponent_row[col].values[0]
                opponent_stats_list.append(opp_data)

        if opponent_stats_list:
            opponent_df = pd.DataFrame(opponent_stats_list)
            df = df.merge(opponent_df, on="Game_ID", how="left")

        return df

    def _add_advanced_stats(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Adds advanced statistics to the game log DataFrame.

        Args:
            df: Game log DataFrame.

        Returns:
            pd.DataFrame: Game log with advanced stats merged.
        """
        advanced_stats_list = []
        game_ids = df["Game_ID"].tolist()

        for game_id in track(game_ids, description="Fetching advanced stats"):
            game_advanced = {}
            game_advanced["Game_ID"] = game_id

            # Get BoxScoreAdvancedV3 data
            try:
                advanced = nba.BoxScoreAdvancedV3(game_id=game_id)
                team_advanced = advanced.get_data_frames()[1]
                team_row = team_advanced[team_advanced["teamId"] == self.id]

                if not team_row.empty:
                    game_advanced["OFF_RATING"] = team_row["offensiveRating"].values[0]
                    game_advanced["DEF_RATING"] = team_row["defensiveRating"].values[0]
                    game_advanced["NET_RATING"] = team_row["netRating"].values[0]
                    game_advanced["PACE"] = team_row["pace"].values[0]
                    game_advanced["EFG_PCT"] = team_row[
                        "effectiveFieldGoalPercentage"
                    ].values[0]
                    game_advanced["TS_PCT"] = team_row["trueShootingPercentage"].values[
                        0
                    ]
                    game_advanced["PIE"] = team_row["PIE"].values[0]
            except Exception:
                pass  # Skip if API call fails

            rate_limiter.wait()  # Rate limiting

            # Get BoxScoreFourFactorsV3 data
            try:
                four_factors = nba.BoxScoreFourFactorsV3(game_id=game_id)
                team_ff = four_factors.get_data_frames()[1]
                team_row = team_ff[team_ff["teamId"] == self.id]

                if not team_row.empty:
                    game_advanced["FT_RATE"] = team_row["freeThrowAttemptRate"].values[
                        0
                    ]
                    game_advanced["TOV_PCT"] = team_row[
                        "teamTurnoverPercentage"
                    ].values[0]
                    game_advanced["OREB_PCT"] = team_row[
                        "offensiveReboundPercentage"
                    ].values[0]
            except Exception:
                pass  # Skip if API call fails

            rate_limiter.wait()  # Rate limiting

            advanced_stats_list.append(game_advanced)

        if advanced_stats_list:
            advanced_df = pd.DataFrame(advanced_stats_list)
            df = df.merge(advanced_df, on="Game_ID", how="left")

        return df
