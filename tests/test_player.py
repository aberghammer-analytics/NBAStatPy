import pandas as pd
import pytest

from nbastatpy.player import Player

PLAYER_NAME = "LeBron James"


def test_player_creation():
    player = Player(PLAYER_NAME)
    assert player.name == PLAYER_NAME


def test_player_get_game_logs_basic():
    """Test basic game logs retrieval."""
    player = Player(PLAYER_NAME)
    game_logs = player.get_game_logs(last_n_games=5)

    assert isinstance(game_logs, pd.DataFrame)
    assert len(game_logs) <= 5
    assert "PTS" in game_logs.columns or "pts" in game_logs.columns


def test_player_get_game_logs_advanced():
    """Test advanced game logs retrieval."""
    player = Player(PLAYER_NAME)
    game_logs = player.get_game_logs(last_n_games=3, measure_type="Advanced")

    assert isinstance(game_logs, pd.DataFrame)
    assert len(game_logs) <= 3


def test_player_get_game_logs_per_mode():
    """Test game logs with different per modes."""
    player = Player(PLAYER_NAME)

    # Per 36 minutes
    game_logs_per36 = player.get_game_logs(last_n_games=3, per_mode="Per36")
    assert isinstance(game_logs_per36, pd.DataFrame)

    # Per 100 possessions
    game_logs_per100 = player.get_game_logs(
        last_n_games=3, per_mode="Per100Possessions"
    )
    assert isinstance(game_logs_per100, pd.DataFrame)


def test_player_get_game_logs_standardize():
    """Test game logs with standardization."""
    player = Player(PLAYER_NAME)
    game_logs = player.get_game_logs(last_n_games=3, standardize=True)

    assert isinstance(game_logs, pd.DataFrame)
    # Standardized columns should be lowercase
    assert all(col == col.lower() for col in game_logs.columns)


def test_player_get_game_logs_invalid_measure_type():
    """Test that invalid measure type raises ValueError."""
    player = Player(PLAYER_NAME)

    with pytest.raises(ValueError, match="Invalid measure_type"):
        player.get_game_logs(measure_type="InvalidType")


def test_player_get_game_logs_invalid_last_n_games_zero():
    """Test that last_n_games=0 raises ValueError."""
    player = Player(PLAYER_NAME)

    with pytest.raises(ValueError, match="last_n_games must be between 1 and 82"):
        player.get_game_logs(last_n_games=0)


def test_player_get_game_logs_invalid_last_n_games_negative():
    """Test that negative last_n_games raises ValueError."""
    player = Player(PLAYER_NAME)

    with pytest.raises(ValueError, match="last_n_games must be between 1 and 82"):
        player.get_game_logs(last_n_games=-5)


def test_player_get_game_logs_invalid_last_n_games_too_large():
    """Test that last_n_games > 82 raises ValueError."""
    player = Player(PLAYER_NAME)

    with pytest.raises(ValueError, match="last_n_games must be between 1 and 82"):
        player.get_game_logs(last_n_games=100)


def test_player_get_game_logs_all_games():
    """Test getting all games with last_n_games=None."""
    player = Player(PLAYER_NAME)
    game_logs = player.get_game_logs(last_n_games=None)

    assert isinstance(game_logs, pd.DataFrame)
    # Should have more than 5 games for an active player
    assert len(game_logs) > 5
