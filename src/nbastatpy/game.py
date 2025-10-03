from typing import List

import nba_api.stats.endpoints as nba
import pandas as pd

from nbastatpy.standardize import standardize_dataframe
from nbastatpy.utils import Formatter


class Game:
    def __init__(self, game_id: str):
        """This represents a game.  Given an ID, you can get boxscore (and other) information through one of the 'get' methods

        Args:
            game_id (str): string with 10 digits
        """
        self.game_id = Formatter.format_game_id(game_id)

    def get_boxscore(self, standardize: bool = False) -> List[pd.DataFrame]:
        """Gets traditional boxscore

        Args:
            standardize: Whether to apply data standardization

        Returns:
            List[pd.DataFrame]: list of dataframes (players, starters/bench, team)
        """
        dfs = nba.BoxScoreTraditionalV3(self.game_id).get_data_frames()

        if standardize:
            dfs = [standardize_dataframe(df, data_type="game") for df in dfs]

        self.boxscore = dfs
        return self.boxscore

    def get_advanced(self):
        """
        Retrieves the advanced box score data for the game.

        Returns:
            pandas.DataFrame: The advanced box score data for the game.
        """
        self.adv_box = nba.BoxScoreAdvancedV3(self.game_id).get_data_frames()
        return self.adv_box

    def get_defense(self):
        """
        Retrieves the defensive statistics for the game.

        Returns:
            def_box (pandas.DataFrame): DataFrame containing the defensive statistics.
        """
        self.def_box = nba.BoxScoreDefensiveV2(self.game_id).get_data_frames()
        return self.def_box

    def get_four_factors(self):
        """
        Retrieves the four factors data for the game.

        Returns:
            pandas.DataFrame: The four factors data for the game.
        """
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
        """
        Retrieves the matchups for the game.

        Returns:
            pandas.DataFrame: The matchups data for the game.
        """
        self.matchups = nba.BoxScoreMatchupsV3(self.game_id).get_data_frames()
        return self.matchups

    def get_misc(self):
        """
        Retrieves miscellaneous box score data for the game.

        Returns:
            pandas.DataFrame: The miscellaneous box score data.
        """
        self.misc = nba.BoxScoreMiscV3(self.game_id).get_data_frames()
        return self.misc

    def get_scoring(self):
        """
        Retrieves the scoring data for the game.

        Returns:
            pandas.DataFrame: The scoring data for the game.
        """
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
        """
        Retrieves the player tracking data for the game.

        Returns:
            playertrack (pandas.DataFrame): The player tracking data for the game.
        """
        self.playertrack = nba.BoxScorePlayerTrackV3(self.game_id).get_data_frames()
        return self.playertrack

    def get_rotations(self):
        """
        Retrieves the rotations data for the game.

        Returns:
            pandas.DataFrame: The rotations data for the game.
        """
        self.rotations = pd.concat(
            nba.GameRotation(game_id=self.game_id).get_data_frames()
        )
        return self.rotations

    def get_playbyplay(self, standardize: bool = False) -> pd.DataFrame:
        """
        Retrieves the play-by-play data for the game.

        Args:
            standardize: Whether to apply data standardization

        Returns:
            pd.DataFrame: The play-by-play data as a pandas DataFrame.
        """
        df = nba.PlayByPlayV3(self.game_id).get_data_frames()[0]

        if standardize:
            df = standardize_dataframe(df, data_type="game")

        self.playbyplay = df
        return self.playbyplay

    def get_win_probability(self) -> pd.DataFrame:
        """
        Retrieves the win probability data for the game.

        Returns:
            pd.DataFrame: The win probability data as a pandas DataFrame.
        """
        self.win_probability = nba.WinProbabilityPBP(
            game_id=self.game_id
        ).get_data_frames()[0]
        return self.win_probability


if __name__ == "__main__":
    GAME_ID = "0022301148"
    game = Game(game_id=GAME_ID)
    print(game.get_win_probability())
