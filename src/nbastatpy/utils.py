from datetime import datetime

import pandas as pd


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


class Formatter:

    def get_current_season_year() -> str:
        current_datetime = datetime.now()
        current_season_year = current_datetime.year
        if current_datetime.month <= 9:
            current_season_year -= 1
        return current_season_year

    def format_season(season_year: int) -> str:
        return "{}-{}".format(int(season_year), str(int(season_year) + 1)[2:])

    def format_game_id(game_id) -> str:
        return str(game_id).zfill(10)

    def combine_strings(row) -> str:
        return next(value for value in row if pd.notna(value))

    def check_playtype(play: str, playtypes: dict) -> str:

        play = play.replace("_", "").replace("-", "").upper()

        if play == "ALL":
            return list(set(playtypes.values()))

        if play not in set(playtypes.keys()):
            raise ValueError(f"Playtype: {play} not found")

        return playtypes[play]
