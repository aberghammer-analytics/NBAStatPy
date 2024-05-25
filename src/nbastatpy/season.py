from io import StringIO
from time import sleep

import nba_api.stats.endpoints as nba
import pandas as pd
import requests
from bs4 import BeautifulSoup
from rich.progress import track

from nbastatpy.utils import Formatter, PlayTypes


class Season:
    def __init__(
        self, season_year: str = None, playoffs=False, permode: str = "PERGAME"
    ):
        self.permode = PlayTypes.PERMODE[
            permode.replace("_", "").replace("-", "").upper()
        ]
        if season_year:
            self.season_year = season_year
        else:
            self.season_year = Formatter.get_current_season_year()

        self.season = Formatter.format_season(self.season_year)
        self.season_type = "Regular Season"
        if playoffs:
            self.season_type = "Playoffs"

    def get_salaries(self) -> pd.DataFrame:
        year = self.season.split("-")[0]
        season_string = year + "-" + str(int(year) + 1)

        url = f"https://hoopshype.com/salaries/players/{season_string}/"
        result = requests.get(url)
        soup = BeautifulSoup(result.content, features="lxml")
        tables = soup.find_all("table")[0].prettify()

        self.salary_df = pd.read_html(StringIO(tables))[0].drop(columns=["Unnamed: 0"])

        return self.salary_df

    def get_lineups(self):
        self.lineups = nba.LeagueDashLineups(
            season=self.season,
            season_type_all_star=self.season_type,
            per_mode_detailed=self.permode,
        ).get_data_frames()[0]
        return self.lineups

    def get_lineup_details(self):
        self.lineup_details = nba.LeagueLineupViz(
            season=self.season,
            season_type_all_star=self.season_type,
            minutes_min=1,
            per_mode_detailed=self.permode,
        ).get_data_frames()[0]
        return self.lineup_details

    def get_opponent_shooting(self):
        self.opponent_shooting = nba.LeagueDashOppPtShot(
            season=self.season,
            season_type_all_star=self.season_type,
            per_mode_simple=self.permode,
        ).get_data_frames()[0]
        return self.opponent_shooting

    def get_player_clutch(self):
        self.player_clutch = nba.LeagueDashPlayerClutch(
            season=self.season,
            season_type_all_star=self.season_type,
            per_mode_detailed=self.permode,
        ).get_data_frames()[0]
        return self.player_clutch

    def get_player_shots(self):
        self.player_shots = nba.LeagueDashPlayerPtShot(
            season=self.season,
            season_type_all_star=self.season_type,
            per_mode_simple=self.permode,
        ).get_data_frames()[0]
        return self.player_shots

    def get_player_shot_locations(self):
        self.player_shot_locations = nba.LeagueDashPlayerShotLocations(
            season=self.season,
            season_type_all_star=self.season_type,
            per_mode_detailed=self.permode,
        ).get_data_frames()[0]
        return self.player_shot_locations

    def get_player_stats(self):
        self.player_stats = nba.LeagueDashPlayerStats(
            season=self.season,
            season_type_all_star=self.season_type,
            per_mode_detailed=self.permode,
        ).get_data_frames()[0]
        return self.player_stats

    def get_team_clutch(self):
        self.team_clutch = nba.LeagueDashTeamClutch(
            season=self.season,
            season_type_all_star=self.season_type,
            per_mode_detailed=self.permode,
        ).get_data_frames()[0]
        return self.team_clutch

    def get_team_shots_bypoint(self):
        self.team_shots_bypoint = nba.LeagueDashTeamPtShot(
            season=self.season,
            season_type_all_star=self.season_type,
            per_mode_simple=self.permode,
        ).get_data_frames()[0]
        return self.team_shots_bypoint

    def get_team_shot_locations(self):
        self.team_shot_locations = nba.LeagueDashTeamShotLocations(
            season=self.season,
            season_type_all_star=self.season_type,
            per_mode_detailed=self.permode,
        ).get_data_frames()[0]
        return self.team_shot_locations

    def get_team_stats(self):
        self.team_stats = nba.LeagueDashTeamStats(
            season=self.season,
            season_type_all_star=self.season_type,
            per_mode_detailed=self.permode,
        ).get_data_frames()[0]
        return self.team_stats

    def get_player_games(self) -> pd.DataFrame:
        self.player_games = nba.PlayerGameLogs(
            season_nullable=self.season,
            season_type_nullable=self.season_type,
            per_mode_simple_nullable=self.permode,
        ).get_data_frames()[0]
        return self.player_games

    def get_team_games(self):
        self.team_games = nba.LeagueGameLog(
            season=self.season,
            season_type_all_star=self.season_type,
            player_or_team_abbreviation="T",
        ).get_data_frames()[0]
        return self.team_games

    def get_player_hustle(self):
        self.player_hustle = nba.LeagueHustleStatsPlayer(
            season=self.season,
            season_type_all_star=self.season_type,
        ).get_data_frames()[0]
        return self.player_hustle

    def get_team_hustle(self):
        self.team_hustle = nba.LeagueHustleStatsTeam(
            season=self.season,
            season_type_all_star=self.season_type,
        ).get_data_frames()[0]
        return self.team_hustle

    def get_player_matchups(self):
        self.player_matchups = nba.LeagueSeasonMatchups(
            season=self.season,
            season_type_playoffs=self.season_type,
            per_mode_simple=self.permode,
        ).get_data_frames()[0]
        return self.player_matchups

    def get_player_estimated_metrics(self):
        self.player_estimated_metrics = nba.PlayerEstimatedMetrics(
            season=self.season,
            season_type=self.season_type,
        ).get_data_frames()[0]
        return self.player_estimated_metrics

    def get_synergy_player(
        self, play_type: str = "Transition", offensive: bool = True
    ) -> pd.DataFrame:
        self.play_type = Formatter.check_playtype(
            play_type, playtypes=PlayTypes.PLAYTYPES
        )
        if offensive:
            self.off_def = "offensive"
        else:
            self.off_def = "defensive"

        if isinstance(self.play_type, str):
            self.synergy = nba.SynergyPlayTypes(
                season=self.season,
                per_mode_simple=self.permode,
                play_type_nullable=self.play_type,
                type_grouping_nullable=self.off_def,
                player_or_team_abbreviation="P",
                season_type_all_star=self.season_type,
            ).get_data_frames()[0]

        else:
            df_list = []
            for play in track(self.play_type):

                temp_df = nba.SynergyPlayTypes(
                    season=self.season,
                    per_mode_simple=self.permode,
                    play_type_nullable=play,
                    type_grouping_nullable=self.off_def,
                    player_or_team_abbreviation="P",
                    season_type_all_star=self.season_type,
                ).get_data_frames()[0]
                df_list.append(temp_df)
                sleep(1)

            self.synergy = pd.concat(df_list)

        return self.synergy

    def get_synergy_team(
        self, play_type: str = "Transition", offensive: bool = True
    ) -> pd.DataFrame:
        self.play_type = Formatter.check_playtype(
            play_type, playtypes=PlayTypes.PLAYTYPES
        )
        if offensive:
            self.off_def = "offensive"
        else:
            self.off_def = "defensive"

        if isinstance(self.play_type, str):
            self.synergy = nba.SynergyPlayTypes(
                season=self.season,
                per_mode_simple=self.permode,
                play_type_nullable=self.play_type,
                type_grouping_nullable=self.off_def,
                player_or_team_abbreviation="T",
                season_type_all_star=self.season_type,
            ).get_data_frames()[0]

        else:
            df_list = []
            for play in track(self.play_type):
                temp_df = nba.SynergyPlayTypes(
                    season=self.season,
                    per_mode_simple=self.permode,
                    play_type_nullable=play,
                    type_grouping_nullable=self.off_def,
                    player_or_team_abbreviation="T",
                    season_type_all_star=self.season_type,
                ).get_data_frames()[0]
                df_list.append(temp_df)
                sleep(1)

            self.synergy = pd.concat(df_list)

        return self.synergy

    def get_tracking_player(
        self,
        track_type: str = "Efficiency",
    ) -> pd.DataFrame:
        self.play_type = Formatter.check_playtype(
            track_type, playtypes=PlayTypes.TRACKING_TYPES
        )

        if isinstance(self.play_type, str):
            self.tracking = nba.LeagueDashPtStats(
                season=self.season,
                per_mode_simple=self.permode,
                pt_measure_type=self.play_type,
                player_or_team="Player",
                season_type_all_star=self.season_type,
            ).get_data_frames()[0]

        else:
            df_list = []
            for play in track(self.play_type):

                temp_df = nba.LeagueDashPtStats(
                    season=self.season,
                    per_mode_simple=self.permode,
                    pt_measure_type=play,
                    player_or_team="Player",
                    season_type_all_star=self.season_type,
                ).get_data_frames()[0]
                df_list.append(temp_df)
                sleep(1)

            self.tracking = pd.concat(df_list)

        return self.tracking

    def get_tracking_team(
        self,
        track_type: str = "Efficiency",
    ) -> pd.DataFrame:
        self.play_type = Formatter.check_playtype(track_type, PlayTypes.TRACKING_TYPES)

        if isinstance(self.play_type, str):
            self.tracking = nba.LeagueDashPtStats(
                season=self.season,
                per_mode_simple=self.permode,
                pt_measure_type=self.play_type,
                player_or_team="Team",
                season_type_all_star=self.season_type,
            ).get_data_frames()[0]

        else:
            df_list = []
            for play in track(self.play_type):

                temp_df = nba.LeagueDashPtStats(
                    season=self.season,
                    per_mode_simple=self.permode,
                    pt_measure_type=play,
                    player_or_team="Team",
                    season_type_all_star=self.season_type,
                ).get_data_frames()[0]
                df_list.append(temp_df)
                sleep(1)

            self.tracking = pd.concat(df_list)

        return self.tracking

    def get_defense_player(
        self,
        defense_type: str = "Overall",
    ) -> pd.DataFrame:
        self.play_type = Formatter.check_playtype(
            defense_type, playtypes=PlayTypes.DEFENSE_TYPES
        )

        if isinstance(self.play_type, str):
            self.defense = nba.LeagueDashPtDefend(
                season=self.season,
                per_mode_simple=self.permode,
                defense_category=self.play_type,
                season_type_all_star=self.season_type,
            ).get_data_frames()[0]

        else:
            df_list = []
            for play in track(self.play_type):

                temp_df = nba.LeagueDashPtDefend(
                    season=self.season,
                    per_mode_simple=self.permode,
                    defense_category=play,
                    season_type_all_star=self.season_type,
                ).get_data_frames()[0]
                df_list.append(temp_df)
                sleep(1)

            self.defense = pd.concat(df_list)

        return self.defense

    def get_defense_team(
        self,
        defense_type: str = "Overall",
    ) -> pd.DataFrame:
        self.play_type = Formatter.check_playtype(
            defense_type, playtypes=PlayTypes.DEFENSE_TYPES
        )

        if isinstance(self.play_type, str):
            self.defense = nba.LeagueDashPtTeamDefend(
                season=self.season,
                per_mode_simple=self.permode,
                defense_category=self.play_type,
                season_type_all_star=self.season_type,
            ).get_data_frames()[0]

        else:
            df_list = []
            for play in track(self.play_type):

                temp_df = nba.LeagueDashPtTeamDefend(
                    season=self.season,
                    per_mode_simple=self.permode,
                    defense_category=play,
                    season_type_all_star=self.season_type,
                ).get_data_frames()[0]
                df_list.append(temp_df)
                sleep(1)

            self.defense = pd.concat(df_list)

        return self.defense


if __name__ == "__main__":
    seas = Season(season_year="2004")
    print(seas.permode)
    print(seas.get_salaries())
