from nbastatpy.game import Game

import pytest

GAME_ID = "0021800836"

def test_game_creation():
    game = Game(GAME_ID)
    assert game.game_id == GAME_ID

def test_playbyplay():
    game = Game(GAME_ID)
    playbyplay = game.get_playbyplay()
    assert playbyplay.shape[0] > 0

def test_boxscore():
    game = Game(GAME_ID)
    boxscore = game.get_boxscore()
    assert boxscore[0].shape[0] > 0