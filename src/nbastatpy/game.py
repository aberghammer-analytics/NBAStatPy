from datetime import date
from io import BytesIO
from typing import List

import nba_api.stats.endpoints as nba
import pandas as pd
import requests
from loguru import logger
from nba_api.stats.endpoints import leaguegamefinder
from nba_api.stats.static import players, teams
from PIL import Image

from utils import Formatter, PlayTypes


class Game:
    def __init__(self, game_id: str):
        """This represents a game.  Given an ID, you can get boxscore (and other) information through one of the 'get' methods

        Args:
            game_id (str): string with 10 digits
        """
        self.game_id = Formatter.format_game_id(game_id)

    def get_boxscore(self) -> List[pd.DataFrame]:
        """Gets traditional boxscore

        Returns:
            List[pd.DataFrame]: list of dataframes (players, starters/bench, team)
        """
        self.boxscore = nba.BoxScoreTraditionalV3(self.game_id).get_data_frames()
        return self.boxscore

    def get_advanced(self):
        self.adv_box = nba.BoxScoreAdvancedV3(self.game_id).get_data_frames()
        return self.adv_box

    def get_defense(self):
        self.def_box = nba.BoxScoreDefensiveV2(self.game_id).get_data_frames()
        return self.def_box

    def get_four_factors(self):
        self.four_factors = nba.BoxScoreFourFactorsV3(self.game_id).get_data_frames()
        return self.four_factors

    def get_hustle(self) -> List[pd.DataFrame]:
        """Gets hustle data for a given game

        Returns:
            List[pd.DataFrame]: list of two dataframes (players, teams)
        """
        self.hustle = nba.BoxScoreHustleV2(self.game_id).get_data_frames()
        return self.hustle

    def get_matchups(self):
        self.matchups = nba.BoxScoreMatchupsV3(self.game_id).get_data_frames()
        return self.matchups

    def get_misc(self):
        self.misc = nba.BoxScoreMiscV3(self.game_id).get_data_frames()
        return self.misc

    def get_scoring(self):
        self.scoring = nba.BoxScoreScoringV3(self.game_id).get_data_frames()
        return self.scoring

    def get_usage(self) -> List[pd.DataFrame]:
        """Gets usage data for a given game

        Returns:
            List[pd.DataFrame]: list of two dataframes (players, teams)
        """
        self.usage = nba.BoxScoreUsageV3(self.game_id).get_data_frames()
        return self.usage

    def get_playertrack(self):
        self.playertrack = nba.BoxScorePlayerTrackV3(self.game_id).get_data_frames()
        return self.playertrack

    def get_rotations(self):
        self.rotations = pd.concat(
            nba.GameRotation(game_id=self.game_id).get_data_frames()
        )
        return self.rotations

    def get_playbyplay(self) -> pd.DataFrame:
        self.playbyplay = nba.PlayByPlayV3(self.game_id).get_data_frames()[0]
        return self.playbyplay

    def get_win_probability(self) -> pd.DataFrame:
        self.win_probability = nba.WinProbabilityPBP(
            game_id=self.game_id
        ).get_data_frames()[0]
        return self.win_probability


if __name__ == "__main__":
    GAME_ID = "0022301148"
    game = Game(game_id=GAME_ID)
    print(game.get_win_probability())
