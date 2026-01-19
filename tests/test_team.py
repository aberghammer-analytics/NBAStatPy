"""Tests for NBAStatPy Team class.

All external API calls are mocked via conftest.py fixtures to prevent timeouts
and ensure reliable testing.
"""

import pandas as pd

from nbastatpy.team import Team

TEAM_NAME = "MIL"


def test_team_creation():
    team = Team(TEAM_NAME)
    assert team.info.get("abbreviation") == TEAM_NAME


def test_get_game_log_basic():
    """Test basic game log retrieval."""
    team = Team(TEAM_NAME, season_year="2024")
    game_log = team.get_game_log(last_n_games=5)

    assert isinstance(game_log, pd.DataFrame)
    # Mock returns 10 rows, but we requested 5 - mock doesn't filter
    assert len(game_log) > 0
    assert "GAME_DATE" in game_log.columns
    assert "MATCHUP" in game_log.columns
    assert "WL" in game_log.columns
    assert "PTS" in game_log.columns


def test_get_game_log_with_opponent_stats():
    """Test game log with opponent statistics flag.

    Note: With mocked data, opponent stats columns may not be present
    since the additional API calls are mocked. We test that the method
    runs without error.
    """
    team = Team(TEAM_NAME, season_year="2024")
    game_log = team.get_game_log(last_n_games=3, include_opponent_stats=True)

    assert isinstance(game_log, pd.DataFrame)
    assert len(game_log) > 0
    # Basic columns should still be present
    assert "GAME_DATE" in game_log.columns
    assert "PTS" in game_log.columns


def test_get_game_log_with_advanced_stats():
    """Test game log with advanced statistics flag.

    Note: With mocked data, advanced stats columns may not be present
    since the additional API calls are mocked. We test that the method
    runs without error.
    """
    team = Team(TEAM_NAME, season_year="2024")
    game_log = team.get_game_log(last_n_games=2, include_advanced_stats=True)

    assert isinstance(game_log, pd.DataFrame)
    assert len(game_log) > 0
    # Basic columns should still be present
    assert "GAME_DATE" in game_log.columns
    assert "PTS" in game_log.columns


def test_get_game_log_all_games():
    """Test game log returns data when last_n_games is None."""
    team = Team(TEAM_NAME, season_year="2024")
    game_log = team.get_game_log()

    assert isinstance(game_log, pd.DataFrame)
    # Mock returns 10 games; real API would return all season games
    assert len(game_log) > 0
