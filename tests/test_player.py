from nbastatpy.player import Player 

import pytest

PLAYER_NAME = "LeBron James"

def test_player_creation():
    player = Player(PLAYER_NAME)
    assert player.name == PLAYER_NAME

def test_player_get_common_info():
    player = Player(PLAYER_NAME)
    player.get_common_info()
    assert player.common_info is not None

def test_player_get_salary():
    player = Player(PLAYER_NAME)
    player.get_salary()
    assert player.salary_df is not None