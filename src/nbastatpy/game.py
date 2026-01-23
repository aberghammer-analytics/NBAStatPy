import nba_api.stats.endpoints as nba
import pandas as pd
from nba_api.live.nba.endpoints import boxscore as live_boxscore

from nbastatpy.config import LeagueID, LiveBoxscoreColumns
from nbastatpy.standardize import standardize_dataframe
from nbastatpy.utils import Formatter


def _flatten_player_stats(players_data: list[dict]) -> pd.DataFrame:
    """Flatten nested statistics from live boxscore player data.

    The live API returns player stats with a nested 'statistics' dictionary.
    This function extracts and flattens that structure into a single-level DataFrame.

    Args:
        players_data: List of player dictionaries from live boxscore API

    Returns:
        pd.DataFrame: Flattened player statistics
    """
    flattened = []
    for player in players_data:
        row = {k: v for k, v in player.items() if k != "statistics" and v != {}}
        if "statistics" in player and isinstance(player["statistics"], dict):
            row.update(player["statistics"])
        flattened.append(row)
    return pd.DataFrame(flattened)


def _build_game_summary(game_data: dict) -> pd.DataFrame:
    """Build a summary DataFrame from live game data.

    Args:
        game_data: Game dictionary from live boxscore API

    Returns:
        pd.DataFrame: Single-row DataFrame with game summary info
    """
    summary = {
        field: game_data.get(field) for field in LiveBoxscoreColumns.SUMMARY_FIELDS
    }
    summary.update(
        {
            "homeTeamId": game_data.get("homeTeam", {}).get("teamId"),
            "homeTeamScore": game_data.get("homeTeam", {}).get("score"),
            "awayTeamId": game_data.get("awayTeam", {}).get("teamId"),
            "awayTeamScore": game_data.get("awayTeam", {}).get("score"),
        }
    )
    return pd.DataFrame([summary])


def _filter_columns(df: pd.DataFrame, columns: list[str]) -> pd.DataFrame:
    """Filter DataFrame to only include columns that exist.

    Args:
        df: Source DataFrame
        columns: List of desired column names

    Returns:
        pd.DataFrame: DataFrame with only the existing columns from the list
    """
    existing_cols = [c for c in columns if c in df.columns]
    return df[existing_cols]


class Game:
    def __init__(self, game_id: str, league: str = "NBA"):
        """This represents a game. Given an ID, you can get boxscore (and other) information through one of the 'get' methods.

        Args:
            game_id (str): String with 10 digits (will be zero-padded if shorter).
            league (str): League identifier ("NBA" or "WNBA"). Defaults to "NBA".
                Required for WNBA games since game IDs don't indicate league.

        Examples:
            >>> game = Game("0021800836")                # NBA game
            >>> game = Game("0041400406", league="WNBA") # WNBA game
        """
        self.game_id = Formatter.format_game_id(game_id)
        self.league = league.upper()
        self.league_id = LeagueID.from_string(self.league)

    def get_boxscore(self, standardize: bool = False) -> list[pd.DataFrame]:
        """Gets traditional boxscore

        Args:
            standardize: Whether to apply data standardization

        Returns:
            list[pd.DataFrame]: list of dataframes (players, starters/bench, team)
        """
        dfs = nba.BoxScoreTraditionalV3(self.game_id).get_data_frames()

        if standardize:
            dfs = [standardize_dataframe(df, data_type="game") for df in dfs]

        self.boxscore = dfs
        return self.boxscore

    def get_advanced(self, standardize: bool = False):
        """
        Retrieves the advanced box score data for the game.

        Args:
            standardize: Whether to apply data standardization

        Returns:
            pandas.DataFrame: The advanced box score data for the game.
        """
        dfs = nba.BoxScoreAdvancedV3(self.game_id).get_data_frames()

        if standardize:
            dfs = [standardize_dataframe(df, data_type="game") for df in dfs]

        self.adv_box = dfs
        return self.adv_box

    def get_defense(self, standardize: bool = False):
        """
        Retrieves the defensive statistics for the game.

        Args:
            standardize: Whether to apply data standardization

        Returns:
            def_box (pandas.DataFrame): DataFrame containing the defensive statistics.
        """
        dfs = nba.BoxScoreDefensiveV2(self.game_id).get_data_frames()

        if standardize:
            dfs = [standardize_dataframe(df, data_type="game") for df in dfs]

        self.def_box = dfs
        return self.def_box

    def get_four_factors(self, standardize: bool = False):
        """
        Retrieves the four factors data for the game.

        Args:
            standardize: Whether to apply data standardization

        Returns:
            pandas.DataFrame: The four factors data for the game.
        """
        dfs = nba.BoxScoreFourFactorsV3(self.game_id).get_data_frames()

        if standardize:
            dfs = [standardize_dataframe(df, data_type="game") for df in dfs]

        self.four_factors = dfs
        return self.four_factors

    def get_hustle(self, standardize: bool = False) -> list[pd.DataFrame]:
        """Gets hustle data for a given game

        Args:
            standardize: Whether to apply data standardization

        Returns:
            list[pd.DataFrame]: list of two dataframes (players, teams)
        """
        dfs = nba.BoxScoreHustleV2(self.game_id).get_data_frames()

        if standardize:
            dfs = [standardize_dataframe(df, data_type="game") for df in dfs]

        self.hustle = dfs
        return self.hustle

    def get_matchups(self, standardize: bool = False):
        """
        Retrieves the matchups for the game.

        Args:
            standardize: Whether to apply data standardization

        Returns:
            pandas.DataFrame: The matchups data for the game.
        """
        dfs = nba.BoxScoreMatchupsV3(self.game_id).get_data_frames()

        if standardize:
            dfs = [standardize_dataframe(df, data_type="game") for df in dfs]

        self.matchups = dfs
        return self.matchups

    def get_misc(self, standardize: bool = False):
        """
        Retrieves miscellaneous box score data for the game.

        Args:
            standardize: Whether to apply data standardization

        Returns:
            pandas.DataFrame: The miscellaneous box score data.
        """
        dfs = nba.BoxScoreMiscV3(self.game_id).get_data_frames()

        if standardize:
            dfs = [standardize_dataframe(df, data_type="game") for df in dfs]

        self.misc = dfs
        return self.misc

    def get_scoring(self, standardize: bool = False):
        """
        Retrieves the scoring data for the game.

        Args:
            standardize: Whether to apply data standardization

        Returns:
            pandas.DataFrame: The scoring data for the game.
        """
        dfs = nba.BoxScoreScoringV3(self.game_id).get_data_frames()

        if standardize:
            dfs = [standardize_dataframe(df, data_type="game") for df in dfs]

        self.scoring = dfs
        return self.scoring

    def get_usage(self, standardize: bool = False) -> list[pd.DataFrame]:
        """Gets usage data for a given game

        Args:
            standardize: Whether to apply data standardization

        Returns:
            list[pd.DataFrame]: list of two dataframes (players, teams)
        """
        dfs = nba.BoxScoreUsageV3(self.game_id).get_data_frames()

        if standardize:
            dfs = [standardize_dataframe(df, data_type="game") for df in dfs]

        self.usage = dfs
        return self.usage

    def get_playertrack(self, standardize: bool = False):
        """
        Retrieves the player tracking data for the game.

        Args:
            standardize: Whether to apply data standardization

        Returns:
            playertrack (pandas.DataFrame): The player tracking data for the game.
        """
        dfs = nba.BoxScorePlayerTrackV3(self.game_id).get_data_frames()

        if standardize:
            dfs = [standardize_dataframe(df, data_type="game") for df in dfs]

        self.playertrack = dfs
        return self.playertrack

    def get_rotations(self, standardize: bool = False):
        """
        Retrieves the rotations data for the game.

        Args:
            standardize: Whether to apply data standardization

        Returns:
            pandas.DataFrame: The rotations data for the game.
        """
        df = pd.concat(
            nba.GameRotation(
                game_id=self.game_id, league_id=self.league_id
            ).get_data_frames()
        )

        if standardize:
            df = standardize_dataframe(df, data_type="game")

        self.rotations = df
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

    def get_win_probability(self, standardize: bool = False) -> pd.DataFrame:
        """
        Retrieves the win probability data for the game.

        Args:
            standardize: Whether to apply data standardization

        Returns:
            pd.DataFrame: The win probability data as a pandas DataFrame.
        """
        df = nba.WinProbabilityPBP(game_id=self.game_id).get_data_frames()[0]

        if standardize:
            df = standardize_dataframe(df, data_type="game")

        self.win_probability = df
        return self.win_probability

    def get_live_boxscore(
        self, stat_type: str = "all", standardize: bool = False
    ) -> list[pd.DataFrame]:
        """Gets live/current boxscore data for the game.

        Works for both in-progress games and completed games.

        Args:
            stat_type: Type of statistics to return. Options:
                - "all": All available data (game info, players, teams)
                - "traditional": Basic player/team stats (points, rebounds, assists)
                - "advanced": Advanced metrics (plus-minus, efficiency)
                - "summary": Game summary only (score, status, time)
            standardize: Whether to apply data standardization

        Returns:
            list[pd.DataFrame]: Live game data based on stat_type
        """
        box = live_boxscore.BoxScore(self.game_id)
        game_data = box.game.get_dict()

        home_players = _flatten_player_stats(box.home_team_player_stats.get_dict())
        away_players = _flatten_player_stats(box.away_team_player_stats.get_dict())
        home_team = pd.DataFrame([box.home_team_stats.get_dict()])
        away_team = pd.DataFrame([box.away_team_stats.get_dict()])

        if stat_type == "summary":
            dfs = [_build_game_summary(game_data)]
        elif stat_type == "traditional":
            dfs = [
                _filter_columns(home_players, LiveBoxscoreColumns.TRADITIONAL),
                _filter_columns(away_players, LiveBoxscoreColumns.TRADITIONAL),
            ]
        elif stat_type == "advanced":
            dfs = [
                _filter_columns(home_players, LiveBoxscoreColumns.ADVANCED),
                _filter_columns(away_players, LiveBoxscoreColumns.ADVANCED),
            ]
        else:  # "all"
            game_info = pd.DataFrame([game_data])
            dfs = [game_info, home_players, away_players, home_team, away_team]

        if standardize:
            dfs = [standardize_dataframe(df, data_type="game") for df in dfs]

        self.live_boxscore = dfs
        return self.live_boxscore
