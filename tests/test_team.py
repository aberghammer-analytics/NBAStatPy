from nbastatpy.team import Team

TEAM_NAME = "MIL"


def test_team_creation():
    team = Team(TEAM_NAME)
    assert team.info.get("abbreviation") == TEAM_NAME


def test_get_game_log_basic():
    """Test basic game log retrieval."""
    team = Team(TEAM_NAME, season_year="2024")
    game_log = team.get_game_log(last_n_games=5)

    assert len(game_log) == 5
    assert "Game_ID" in game_log.columns
    assert "GAME_DATE" in game_log.columns
    assert "MATCHUP" in game_log.columns
    assert "WL" in game_log.columns
    assert "PTS" in game_log.columns


def test_get_game_log_with_opponent_stats():
    """Test game log with opponent statistics included."""
    team = Team(TEAM_NAME, season_year="2024")
    game_log = team.get_game_log(last_n_games=3, include_opponent_stats=True)

    assert len(game_log) == 3
    # Check for opponent stat columns
    assert "OPP_PTS" in game_log.columns
    assert "OPP_REB" in game_log.columns
    assert "OPP_AST" in game_log.columns
    assert "OPP_FG_PCT" in game_log.columns


def test_get_game_log_with_advanced_stats():
    """Test game log with advanced statistics included.

    Note: This test makes multiple API calls and may be slower.
    """
    team = Team(TEAM_NAME, season_year="2024")
    game_log = team.get_game_log(last_n_games=2, include_advanced_stats=True)

    assert len(game_log) == 2
    # Check for advanced stat columns
    assert "OFF_RATING" in game_log.columns
    assert "DEF_RATING" in game_log.columns
    assert "NET_RATING" in game_log.columns
    assert "PACE" in game_log.columns


def test_get_game_log_all_games():
    """Test game log returns all games when last_n_games is None."""
    team = Team(TEAM_NAME, season_year="2024")
    game_log = team.get_game_log()

    # Should have many games for a full season
    assert len(game_log) > 50
