from nbastatpy.season import Season

import pytest

SEASON_YEAR = "2020"

def test_season_creation():
    season = Season(SEASON_YEAR)
    assert season.season_year== SEASON_YEAR

def test_lineups():
    season = Season(SEASON_YEAR)
    lineups = season.get_lineups()
    assert lineups.shape[0] > 0

def test_salaries():
    season = Season(SEASON_YEAR)
    salaries = season.get_salaries()
    assert salaries.shape[0] > 0