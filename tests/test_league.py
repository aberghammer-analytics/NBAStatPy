from nbastatpy.league import League

SEASON_YEAR = "2020"


def test_league_creation():
    league = League(SEASON_YEAR)
    assert league.season_year == int(SEASON_YEAR)
