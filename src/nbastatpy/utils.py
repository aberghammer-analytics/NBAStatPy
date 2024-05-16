import pandas as pd


class Formatter:

    def format_season(season_year: int) -> str:
        return "{}-{}".format(int(season_year), str(int(season_year) + 1)[2:])

    def format_game_id(game_id) -> str:
        return str(game_id).zfill(10)

    def combine_strings(row) -> str:
        return next(value for value in row if pd.notna(value))
