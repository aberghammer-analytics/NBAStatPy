from time import sleep

import nba_api.stats.endpoints as nba
import pandas as pd
from rich.progress import track

from utils import Formatter


class Season:
    def __init__(self, season_year: str = None, playoffs=False):
        if season_year:
            self.season_year = season_year
        else:
            self.season_year = Formatter.get_current_season_year()

        self.season = Formatter.format_season(self.season_year)
        self.season_type = "Regular Season"
        if playoffs:
            self.season_type = "Playoffs"

    def get_lineups(self):
        self.lineups = nba.LeagueDashLineups(
            season=self.season, season_type_all_star=self.season_type
        ).get_data_frames()[0]
        return self.lineups

    def get_lineup_details(self):
        self.lineup_details = nba.LeagueLineupViz(
            season=self.season, season_type_all_star=self.season_type, minutes_min=1
        ).get_data_frames()[0]
        return self.lineup_details

    def get_opponent_shooting(self):
        self.opponent_shooting = nba.LeagueDashOppPtShot(
            season=self.season, season_type_all_star=self.season_type
        ).get_data_frames()[0]
        return self.opponent_shooting

    def get_player_clutch(self):
        self.player_clutch = nba.LeagueDashPlayerClutch(
            season=self.season, season_type_all_star=self.season_type
        ).get_data_frames()[0]
        return self.player_clutch

    def get_player_shots(self):
        self.player_shots = nba.LeagueDashPlayerPtShot(
            season=self.season, season_type_all_star=self.season_type
        ).get_data_frames()[0]
        return self.player_shots

    def get_player_shot_locations(self):
        self.player_shot_locations = nba.LeagueDashPlayerShotLocations(
            season=self.season, season_type_all_star=self.season_type
        ).get_data_frames()[0]
        return self.player_shot_locations

    def get_player_stats(self):
        self.player_stats = nba.LeagueDashPlayerStats(
            season=self.season, season_type_all_star=self.season_type
        ).get_data_frames()[0]
        return self.player_stats

    def get_player_point_defend(self):
        self.player_point_defend = nba.LeagueDashPtDefend(
            season=self.season, season_type_all_star=self.season_type
        ).get_data_frames()[0]
        return self.player_point_defend

    def get_team_distance(self):
        self.team_distance = nba.LeagueDashPtStats(
            season=self.season, season_type_all_star=self.season_type
        ).get_data_frames()[0]
        return self.team_distance

    def get_team_defense(self):
        self.team_defense = nba.LeagueDashPtTeamDefend(
            season=self.season, season_type_all_star=self.season_type
        ).get_data_frames()[0]
        return self.team_defense

    def get_team_clutch(self):
        self.team_clutch = nba.LeagueDashTeamClutch(
            season=self.season, season_type_all_star=self.season_type
        ).get_data_frames()[0]
        return self.team_clutch

    def get_team_shots_bypoint(self):
        self.team_shots_bypoint = nba.LeagueDashTeamPtShot(
            season=self.season, season_type_all_star=self.season_type
        ).get_data_frames()[0]
        return self.team_shots_bypoint

    def get_team_shot_locations(self):
        self.team_shot_locations = nba.LeagueDashTeamShotLocations(
            season=self.season, season_type_all_star=self.season_type
        ).get_data_frames()[0]
        return self.team_shot_locations

    def get_team_stats(self):
        self.team_stats = nba.LeagueDashTeamStats(
            season=self.season, season_type_all_star=self.season_type
        ).get_data_frames()[0]
        return self.team_stats

    def get_player_games(self) -> pd.DataFrame:
        self.player_games = nba.PlayerGameLogs(
            season_nullable=self.season, season_type_nullable=self.season_type
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
            season=self.season, season_type_all_star=self.season_type
        ).get_data_frames()[0]
        return self.player_hustle

    def get_team_hustle(self):
        self.team_hustle = nba.LeagueHustleStatsTeam(
            season=self.season, season_type_all_star=self.season_type
        ).get_data_frames()[0]
        return self.team_hustle

    def get_player_matchups(self):
        self.player_matchups = nba.LeagueSeasonMatchups(
            season=self.season, season_type_playoffs=self.season_type
        ).get_data_frames()[0]
        return self.player_matchups

    def get_player_estimated_metrics(self):
        self.player_estimated_metrics = nba.PlayerEstimatedMetrics(
            season=self.season, season_type=self.season_type
        ).get_data_frames()[0]
        return self.player_estimated_metrics

    def get_synergy_player(
        self, play_type: str = "Transition", offensive: bool = True
    ) -> pd.DataFrame:
        self.play_type = Formatter.check_playtype(play_type)
        if offensive:
            self.off_def = "offensive"
        else:
            self.off_def = "defensive"

        if isinstance(self.play_type, str):
            self.synergy = nba.SynergyPlayTypes(
                season=self.season,
                per_mode_simple="PerGame",
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
                    per_mode_simple="PerGame",
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
        self.play_type = Formatter.check_playtype(play_type)
        if offensive:
            self.off_def = "offensive"
        else:
            self.off_def = "defensive"

        if isinstance(self.play_type, str):
            self.synergy = nba.SynergyPlayTypes(
                season=self.season,
                per_mode_simple="PerGame",
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
                    per_mode_simple="PerGame",
                    play_type_nullable=play,
                    type_grouping_nullable=self.off_def,
                    player_or_team_abbreviation="T",
                    season_type_all_star=self.season_type,
                ).get_data_frames()[0]
                df_list.append(temp_df)
                sleep(1)

            self.synergy = pd.concat(df_list)

        return self.synergy


if __name__ == "__main__":
    seas = Season()
    print(seas.get_synergy_player("All", False))
