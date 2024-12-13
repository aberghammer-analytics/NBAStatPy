from nbastatpy.team import Team

import pytest 

TEAM_NAME = "MIL"

def test_team_creation():
    team = Team(TEAM_NAME)
    assert team.info.get("abbreviation") == TEAM_NAME

def test_team_roster():
    team = Team(TEAM_NAME)
    team.get_roster()
    assert team.roster is not None

def test_team_logo():
    team = Team(TEAM_NAME)
    team.get_logo()
    assert team.logo is not None

def test_team_salary():
    team = Team(TEAM_NAME, season_year="2020")
    team.get_salary()
    assert team.salary_df is not None