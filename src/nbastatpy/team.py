from io import BytesIO
from typing import List

import nba_api.stats.endpoints as nba
import pandas as pd
import requests
from cairosvg import svg2png
from nba_api.stats.static import teams
from PIL import Image

from utils import Formatter, PlayTypes


class Team:
    def __init__(
        self,
        team_abbreviation: str,
        season_year: str = None,
        playoffs=False,
        permode: str = "PerGame",
    ):
        self.permode = PlayTypes.PERMODE[
            permode.replace("_", "").replace("-", "").upper()
        ]
        if season_year:
            self.season_year = season_year
        else:
            self.season_year = Formatter.get_current_season_year()

        self.info = teams.find_team_by_abbreviation(team_abbreviation)

        self.season = Formatter.format_season(self.season_year)
        self.season_type = "Regular Season"
        if playoffs:
            self.season_type = "Playoffs"

        for attr_name, value in self.info.items():
            setattr(self, attr_name.lower(), self.info.get(attr_name, None))

    def get_logo(self):
        pic_url = f"https://cdn.nba.com/logos/nba/{self.id}/primary/L/logo.svg"
        pic = requests.get(pic_url)
        pic = svg2png(bytestring=pic.content, write_to=None)
        self.logo = Image.open(BytesIO(pic))
        return self.logo

    def get_roster(self) -> List[pd.DataFrame]:
        self.roster = nba.CommonTeamRoster(
            self.id,
            season=self.season,
        ).get_data_frames()
        return self.roster

    def get_year_by_year(self) -> pd.DataFrame():
        self.year_by_year = nba.TeamYearByYearStats(
            team_id=self.id, per_mode_simple=self.permode
        ).get_data_frames()[0]
        return self.year_by_year

    def get_general_splits(self) -> pd.DataFrame:
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
            ).get_data_frames()
        ).drop(columns=drop_cols)
        return self.general_splits

    def get_shooting_splits(self) -> pd.DataFrame:
        self.shooting_splits = pd.concat(
            nba.TeamDashboardByShootingSplits(
                team_id=self.id,
                season=self.season,
                season_type_all_star=self.season_type,
                per_mode_detailed=self.permode,
            ).get_data_frames()
        )
        return self.shooting_splits

    def get_leaders(self) -> pd.DataFrame:
        self.leaders = nba.FranchiseLeaders(team_id=self.id).get_data_frames()[0]
        return self.leaders

    def get_franchise_players(self) -> pd.DataFrame:
        self.franchise_players = nba.FranchisePlayers(
            team_id=self.id
        ).get_data_frames()[0]
        return self.franchise_players

    def get_season_lineups(self) -> pd.DataFrame:
        self.season_lineups = nba.LeagueDashLineups(
            team_id_nullable=self.id,
            season=self.season,
            season_type_all_star=self.season_type,
            per_mode_detailed=self.permode,
        ).get_data_frames()[0]
        self.season_lineups["season"] = self.season
        self.season_lineups["season_type"] = self.season_type

        return self.season_lineups

    def get_opponent_shooting(self) -> pd.DataFrame:
        self.opponent_shooting = nba.LeagueDashOppPtShot(
            team_id_nullable=self.id,
            season=self.season,
            season_type_all_star=self.season_type,
            per_mode_simple=self.permode,
        ).get_data_frames()[0]
        self.opponent_shooting["season"] = self.season
        self.opponent_shooting["season_type"] = self.season_type

        return self.opponent_shooting

    def get_player_clutch(self) -> pd.DataFrame:
        self.player_clutch = nba.LeagueDashPlayerClutch(
            team_id_nullable=self.id,
            season=self.season,
            season_type_all_star=self.season_type,
            per_mode_detailed=self.permode,
        ).get_data_frames()[0]
        self.player_clutch["season"] = self.season
        self.player_clutch["season_type"] = self.season_type

        return self.player_clutch

    def get_player_shots(self) -> pd.DataFrame:
        self.player_shots = nba.LeagueDashPlayerPtShot(
            team_id_nullable=self.id,
            season=self.season,
            season_type_all_star=self.season_type,
            per_mode_simple=self.permode,
        ).get_data_frames()[0]
        self.player_shots["season"] = self.season
        self.player_shots["season_type"] = self.season_type

        return self.player_shots

    def get_player_shot_locations(self) -> pd.DataFrame:
        self.player_shot_locations = nba.LeagueDashPlayerShotLocations(
            team_id_nullable=self.id,
            season=self.season,
            season_type_all_star=self.season_type,
            per_mode_detailed=self.permode,
        ).get_data_frames()[0]
        self.player_shot_locations["season"] = self.season
        self.player_shot_locations["season_type"] = self.season_type

        return self.player_shot_locations

    def get_player_stats(self) -> pd.DataFrame:
        self.player_stats = nba.LeagueDashPlayerStats(
            team_id_nullable=self.id,
            season=self.season,
            season_type_all_star=self.season_type,
            per_mode_detailed=self.permode,
        ).get_data_frames()[0]
        self.player_stats["season"] = self.season
        self.player_stats["season_type"] = self.season_type

        return self.player_stats

    def get_player_point_defend(self) -> pd.DataFrame:
        self.player_point_defend = nba.LeagueDashPtDefend(
            team_id_nullable=self.id,
            season=self.season,
            season_type_all_star=self.season_type,
            per_mode_simple=self.permode,
        ).get_data_frames()[0]
        self.player_point_defend["season"] = self.season
        self.player_point_defend["season_type"] = self.season_type

        return self.player_point_defend

    def get_player_hustle(self) -> pd.DataFrame:
        self.player_hustle = nba.LeagueHustleStatsPlayer(
            team_id_nullable=self.id,
            season=self.season,
            season_type_all_star=self.season_type,
        ).get_data_frames()[0]
        self.player_hustle["season"] = self.season
        self.player_hustle["season_type"] = self.season_type

        return self.player_hustle

    def get_lineup_details(self) -> pd.DataFrame:
        self.lineup_details = nba.LeagueLineupViz(
            team_id_nullable=self.id,
            season=self.season,
            season_type_all_star=self.season_type,
            minutes_min=1,
            per_mode_detailed=self.permode,
        ).get_data_frames()[0]
        self.lineup_details["season"] = self.season
        self.lineup_details["season_type"] = self.season_type

        return self.lineup_details

    def get_player_on_details(self) -> pd.DataFrame:
        self.player_on_details = nba.LeaguePlayerOnDetails(
            team_id=self.id,
            season=self.season,
            season_type_all_star=self.season_type,
            per_mode_detailed=self.permode,
        ).get_data_frames()[0]
        self.player_on_details["season"] = self.season
        self.player_on_details["season_type"] = self.season_type

        return self.player_on_details

    def get_player_matchups(self, defense=False) -> pd.DataFrame:
        if defense:
            self.player_matchups = nba.LeagueSeasonMatchups(
                def_team_id_nullable=self.id,
                season=self.season,
                season_type_playoffs=self.season_type,
                per_mode_simple=self.permode,
            ).get_data_frames()[0]
        else:
            self.player_matchups = nba.LeagueSeasonMatchups(
                off_team_id_nullable=self.id,
                season=self.season,
                season_type_playoffs=self.season_type,
                per_mode_simple=self.permode,
            ).get_data_frames()[0]

        self.player_matchups["season"] = self.season
        self.player_matchups["season_type"] = self.season_type

        return self.player_matchups

    def get_player_passes(self) -> pd.DataFrame:
        self.player_passes = pd.concat(
            nba.TeamDashPtPass(
                team_id=self.id,
                season=self.season,
                season_type_all_star=self.season_type,
                per_mode_simple=self.permode,
            ).get_data_frames()
        )

        group_cols = ["PASS_FROM", "PASS_TO"]
        self.player_passes["GROUP_SET"] = self.player_passes[group_cols].apply(
            Formatter.combine_strings, axis=1
        )
        self.player_passes = self.player_passes.drop(columns=group_cols)
        return self.player_passes.reset_index(drop=True)

    def get_player_onoff(self) -> pd.DataFrame:
        self.player_onoff = pd.concat(
            nba.TeamPlayerOnOffDetails(
                team_id=team.id,
                season=self.season,
                season_type_all_star=self.season_type,
                per_mode_detailed=self.permode,
            ).get_data_frames()[1:]
        )
        return self.player_onoff.reset_index(drop=True)


if __name__ == "__main__":
    team_name = "MIL"
    team = Team(team_name, season_year="2020", playoffs=True)
    print(team.get_year_by_year())
