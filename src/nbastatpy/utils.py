from datetime import datetime

import pandas as pd


class LeaderStats:
    """Mapping for league leader stat categories."""

    STAT_CATEGORIES = {
        # User-friendly names -> API abbreviations
        "POINTS": "PTS",
        "PTS": "PTS",
        "REBOUNDS": "REB",
        "REB": "REB",
        "ASSISTS": "AST",
        "AST": "AST",
        "STEALS": "STL",
        "STL": "STL",
        "BLOCKS": "BLK",
        "BLK": "BLK",
        "FIELDGOALPCT": "FG_PCT",
        "FG_PCT": "FG_PCT",
        "FGPCT": "FG_PCT",
        "THREEPOINTPCT": "FG3_PCT",
        "FG3_PCT": "FG3_PCT",
        "FG3PCT": "FG3_PCT",
        "FREETHROWPCT": "FT_PCT",
        "FT_PCT": "FT_PCT",
        "FTPCT": "FT_PCT",
        "FGM": "FGM",
        "FGA": "FGA",
        "FG3M": "FG3M",
        "FG3A": "FG3A",
        "FTM": "FTM",
        "FTA": "FTA",
        "OREB": "OREB",
        "DREB": "DREB",
        "TURNOVERS": "TOV",
        "TOV": "TOV",
        "GAMESPLAYED": "GP",
        "GP": "GP",
    }

    # Map stat abbreviation -> AllTimeLeadersGrids attribute name
    ALLTIME_ATTR_MAP = {
        "PTS": "pts_leaders",
        "AST": "ast_leaders",
        "REB": "reb_leaders",
        "STL": "stl_leaders",
        "BLK": "blk_leaders",
        "FGM": "fgm_leaders",
        "FGA": "fga_leaders",
        "FG_PCT": "fg_pct_leaders",
        "FG3M": "fg3_m_leaders",
        "FG3A": "fg3_a_leaders",
        "FG3_PCT": "fg3_pct_leaders",
        "FTM": "ftm_leaders",
        "FTA": "fta_leaders",
        "FT_PCT": "ft_pct_leaders",
        "OREB": "oreb_leaders",
        "DREB": "dreb_leaders",
        "TOV": "tov_leaders",
        "GP": "g_p_leaders",
    }


class PlayTypes:
    PERMODE = {
        "PERGAME": "PerGame",
        "PER36": "Per36",
        "TOTALS": "Totals",
        "PERMINUTE": "PerMinute",
        "PERMIN": "PerMinute",
        "PERPOSSESSION": "Per100Possessions",
        "PERPOSS": "Per100Possessions",
        "PER100POSSESSIONS": "Per100Possessions",
        "PERPLAY": "PerPlay",
        "PER100PLAYS": "Per100Plays",
    }

    PLAYTYPES = {
        "TRANSITION": "Transition",
        "ISOLATION": "Isolation",
        "ISO": "Isolation",
        "PRBALLHANDLER": "PRBallHandler",
        "PRROLLMAN": "PRRollman",
        "POSTUP": "Postup",
        "SPOTUP": "Spotup",
        "HANDOFF": "Handoff",
        "CUT": "Cut",
        "OFFSCREEN": "OffScreen",
        "PUTBACKS": "OffRebound",
        "OFFREBOUND": "OffRebound",
        "MISC": "Misc",
    }

    TRACKING_TYPES = {
        "SPEEDDISTANCE": "SpeedDistance",
        "SPEED": "SpeedDistance",
        "DISTANCE": "SpeedDistance",
        "POSSESSIONS": "Possessions",
        "CATCHSHOOT": "CatchShoot",
        "PULLUPSHOT": "PullUpShot",
        "PULLUP": "PullUpShot",
        "DEFENSE": "Defense",
        "DRIVES": "Drives",
        "DRIVE": "Drives",
        "PASSING": "Passing",
        "ELBOWTOUCH": "ElbowTouch",
        "ELBOW": "ElbowTouch",
        "POSTTOUCH": "PostTouch",
        "POST": "PostTouch",
        "PAINTTOUCH": "PaintTouch",
        "PAINT": "PaintTouch",
        "EFFICIENCY": "Efficiency",
    }

    DEFENSE_TYPES = {
        "OVERALL": "Overall",
        "THREE": "3 Pointers",
        "THREES": "3 Pointers",
        "TWOS": "2 Pointers",
        "TWO": "2 Pointers",
        "LESSTHAN6FT": "Less Than 6Ft",
        "LESSTHAN10FT": "Less Than 10Ft",
        "GREATERTHAN15FT": "Greater Than 15Ft",
    }


class MeasureTypes:
    """Mapping for player game log measure types."""

    TYPES = {
        "BASE": "Base",
        "BASIC": "Base",
        "TRADITIONAL": "Base",
        "ADVANCED": "Advanced",
        "ADV": "Advanced",
        "MISC": "Misc",
        "MISCELLANEOUS": "Misc",
        "SCORING": "Scoring",
        "USAGE": "Usage",
    }


class GameStatsColumns:
    """Column definitions for game statistics output."""

    # Columns to include in team stats output
    TEAM_STATS = [
        "pts",
        "reb",
        "ast",
        "stl",
        "blk",
        "tov",
        "pf",
        "fgm",
        "fga",
        "fg_pct",
        "fg3m",
        "fg3a",
        "fg3_pct",
        "ftm",
        "fta",
        "ft_pct",
        "oreb",
        "dreb",
        "plus_minus",
    ]

    # Columns to include in player stats output
    PLAYER_STATS = [
        "player_id",
        "player_name",
        "team_abbreviation",
        "min",
        "pts",
        "reb",
        "ast",
        "stl",
        "blk",
        "tov",
        "pf",
        "fgm",
        "fga",
        "fg_pct",
        "fg3m",
        "fg3a",
        "fg3_pct",
        "ftm",
        "fta",
        "ft_pct",
        "oreb",
        "dreb",
        "plus_minus",
    ]


class Formatter:
    @staticmethod
    def get_current_season_year() -> str:
        current_datetime = datetime.now()
        current_season_year = current_datetime.year
        if current_datetime.month <= 9:
            current_season_year -= 1
        return current_season_year

    @staticmethod
    def normalize_season_year(season_input) -> int:
        """
        Normalize various season year inputs to a 4-digit year.

        Args:
            season_input: Can be int or str. Examples: 2022, "2022", 22, "22", "2022-23"

        Returns:
            int: The starting year of the season (e.g., 2022 for 2022-23 season)
        """
        # Convert to string for uniform processing
        season_str = str(season_input).strip()

        # Handle full season format like "2022-23"
        if "-" in season_str:
            return int(season_str.split("-")[0])

        # Convert to integer
        year = int(season_str)

        # If 2-digit year, convert to 4-digit
        if year < 100:
            # Assume years 00-49 are 2000-2049, 50-99 are 1950-1999
            if year < 50:
                year += 2000
            else:
                year += 1900

        return year

    @staticmethod
    def format_season(season_year: int) -> str:
        return "{}-{}".format(int(season_year), str(int(season_year) + 1)[2:])

    @staticmethod
    def format_season_id(season_input) -> str:
        """
        Convert any season format to YYYYYYYY format (8 digits representing two years).

        Args:
            season_input: Can be int, str. Examples: 2022, "2022", "2022-23", "22-23", 20222023

        Returns:
            str: 8-digit season ID (e.g., "20222023" for 2022-23 season)

        Examples:
            >>> Formatter.format_season_id(2022)
            "20222023"
            >>> Formatter.format_season_id("2022-23")
            "20222023"
            >>> Formatter.format_season_id(20222023)
            "20222023"
        """
        season_str = str(season_input).strip()

        # Already in YYYYYYYY format
        if len(season_str) == 8 and season_str.isdigit():
            return season_str

        # Handle formats with hyphen (e.g., "2022-23" or "22-23")
        if "-" in season_str:
            parts = season_str.split("-")
            first_year = Formatter.normalize_season_year(parts[0])
            # Second part could be 2-digit or 4-digit
            if len(parts[1]) == 2:
                second_year = first_year + 1
            else:
                second_year = int(parts[1])
            return f"{first_year}{second_year}"

        # Single year input - assume it's the starting year
        year = Formatter.normalize_season_year(season_input)
        return f"{year}{year + 1}"

    @staticmethod
    def format_game_id(game_id) -> str:
        return str(game_id).zfill(10)

    @staticmethod
    def combine_strings(row) -> str:
        return next(value for value in row if pd.notna(value))

    @staticmethod
    def check_playtype(play: str, playtypes: dict) -> str:
        play = play.replace("_", "").replace("-", "").upper()

        if play == "ALL":
            return list(set(playtypes.values()))

        if play not in set(playtypes.keys()):
            raise ValueError(f"Playtype: {play} not found")

        return playtypes[play]

    @staticmethod
    def normalize_season(season: str) -> str:
        """Convert various season formats to YYYYYYYY."""
        s = season.replace("-", "").replace(" ", "")

        if len(s) == 8 and s.isdigit():
            return s
        if len(s) == 4 and s.isdigit():
            first_two = s[:2]
            if first_two in ["19", "20"]:
                # Full year like "2024" -> "20242025"
                year = int(s)
                return f"{year}{year + 1}"
            else:
                # Shortened format like "2324" from "23-24" -> "20232024"
                return f"20{s[:2]}20{s[2:]}"
        if len(s) == 6 and s.isdigit():
            # "202324" -> "20232024"
            start_year = s[:4]
            end_year_suffix = s[4:]
            return f"{start_year}20{end_year_suffix}"

        return s
