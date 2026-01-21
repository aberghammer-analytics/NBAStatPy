"""Shared pytest fixtures for NBAStatPy tests.

Contains mock fixtures for NBA API calls used across multiple test files.
"""

from datetime import datetime, timedelta
from unittest.mock import MagicMock

import pandas as pd
import pytest


# ============================================================================
# Mock Data Fixtures - Used by MCP tools and server tests
# ============================================================================


@pytest.fixture(autouse=True)
def mock_requests_get(mocker):
    """Mock requests.get for salary web scraping."""
    # Create mock HTML response for salary data
    # The header row uses <th> tags, so find_all("td") returns empty for header row
    # This matches the real hoopshype.com structure
    mock_html = """
    <html>
    <body>
    <table></table>
    <table></table>
    <table>
        <tr><th>Season</th><th>Team</th><th>Salary</th></tr>
        <tr><td>2024-25</td><td>LAL</td><td>$47,607,350</td></tr>
        <tr><td>2025-26</td><td>LAL</td><td>$50,434,788</td></tr>
    </table>
    <table>
        <tr><th>Season</th><th>Team</th><th>Salary</th></tr>
        <tr><td>2023-24</td><td>LAL</td><td>$47,000,000</td></tr>
        <tr><td>2022-23</td><td>LAL</td><td>$44,474,988</td></tr>
    </table>
    </body>
    </html>
    """
    mock_response = MagicMock()
    mock_response.content = mock_html.encode()
    mocker.patch("requests.get", return_value=mock_response)
    return mock_response


@pytest.fixture(autouse=True)
def mock_player_game_logs(mocker):
    """Mock PlayerGameLogs API call."""
    # Create realistic game log data
    today = datetime.now()
    dates = [(today - timedelta(days=i)).strftime("%Y-%m-%d") for i in range(10)]

    mock_df = pd.DataFrame(
        {
            "SEASON_YEAR": ["2024-25"] * 10,
            "PLAYER_ID": [2544] * 10,
            "PLAYER_NAME": ["LeBron James"] * 10,
            "TEAM_ID": [1610612747] * 10,
            "TEAM_ABBREVIATION": ["LAL"] * 10,
            "TEAM_NAME": ["Los Angeles Lakers"] * 10,
            "GAME_ID": [f"002240050{i}" for i in range(10)],
            "GAME_DATE": dates,
            "MATCHUP": [
                "LAL vs. BOS",
                "LAL @ MIA",
                "LAL vs. DEN",
                "LAL @ PHX",
                "LAL vs. GSW",
            ]
            * 2,
            "WL": ["W", "L"] * 5,
            "MIN": [35.5] * 10,
            "FGM": [10] * 10,
            "FGA": [18] * 10,
            "FG_PCT": [0.556] * 10,
            "FG3M": [2] * 10,
            "FG3A": [5] * 10,
            "FG3_PCT": [0.400] * 10,
            "FTM": [6] * 10,
            "FTA": [8] * 10,
            "FT_PCT": [0.750] * 10,
            "OREB": [1] * 10,
            "DREB": [7] * 10,
            "REB": [8] * 10,
            "AST": [9] * 10,
            "TOV": [3] * 10,
            "STL": [2] * 10,
            "BLK": [1] * 10,
            "BLKA": [0] * 10,
            "PF": [2] * 10,
            "PFD": [5] * 10,
            "PTS": [28] * 10,
            "PLUS_MINUS": [12] * 10,
        }
    )
    mock_response = MagicMock()
    mock_response.get_data_frames.return_value = [mock_df]
    mocker.patch("nba_api.stats.endpoints.PlayerGameLogs", return_value=mock_response)
    return mock_df


@pytest.fixture(autouse=True)
def mock_league_dash_player_stats(mocker):
    """Mock LeagueDashPlayerStats API call for league leaders."""
    mock_df = pd.DataFrame(
        {
            "PLAYER_ID": [201566, 203507, 2544, 201142, 203954],
            "PLAYER_NAME": [
                "Kevin Durant",
                "Giannis Antetokounmpo",
                "LeBron James",
                "Kevin Love",
                "Joel Embiid",
            ],
            "TEAM_ID": [1610612756, 1610612749, 1610612747, 1610612748, 1610612755],
            "TEAM_ABBREVIATION": ["PHX", "MIL", "LAL", "MIA", "PHI"],
            "AGE": [35, 29, 39, 36, 30],
            "GP": [50, 52, 48, 40, 35],
            "W": [30, 35, 28, 25, 22],
            "L": [20, 17, 20, 15, 13],
            "W_PCT": [0.600, 0.673, 0.583, 0.625, 0.629],
            "MIN": [35.5, 32.8, 35.2, 25.5, 33.8],
            "FGM": [10.2, 11.5, 9.8, 4.2, 10.5],
            "FGA": [18.5, 20.2, 18.0, 9.5, 18.8],
            "FG_PCT": [0.551, 0.569, 0.544, 0.442, 0.559],
            "FG3M": [2.0, 1.2, 2.5, 2.8, 1.5],
            "FG3A": [5.5, 4.0, 6.5, 7.0, 4.2],
            "FG3_PCT": [0.364, 0.300, 0.385, 0.400, 0.357],
            "FTM": [5.5, 6.8, 4.2, 2.5, 10.2],
            "FTA": [6.2, 9.5, 5.5, 3.0, 11.8],
            "FT_PCT": [0.887, 0.716, 0.764, 0.833, 0.864],
            "OREB": [0.5, 2.2, 1.0, 1.5, 2.8],
            "DREB": [6.0, 9.8, 7.0, 5.5, 8.2],
            "REB": [6.5, 12.0, 8.0, 7.0, 11.0],
            "AST": [5.0, 6.5, 8.5, 2.0, 4.5],
            "TOV": [3.0, 3.5, 3.2, 1.5, 3.8],
            "STL": [0.8, 1.0, 1.2, 0.5, 1.0],
            "BLK": [1.2, 1.5, 0.8, 0.3, 1.8],
            "BLKA": [0.5, 0.8, 0.5, 0.3, 0.8],
            "PF": [2.0, 2.8, 1.8, 2.2, 3.0],
            "PFD": [5.0, 7.5, 4.5, 2.5, 8.5],
            "PTS": [28.0, 31.0, 26.5, 14.0, 32.5],
            "PLUS_MINUS": [5.5, 8.2, 4.0, 2.5, 6.8],
            "NBA_FANTASY_PTS": [45.5, 52.0, 42.0, 25.5, 48.5],
            "DD2": [15, 35, 25, 10, 30],
            "TD3": [2, 8, 5, 0, 3],
            "GP_RANK": [5, 3, 7, 15, 20],
            "W_RANK": [8, 5, 12, 15, 18],
            "L_RANK": [12, 17, 12, 15, 13],
            "W_PCT_RANK": [15, 8, 18, 12, 10],
            "MIN_RANK": [5, 12, 6, 45, 10],
            "FGM_RANK": [8, 5, 12, 55, 6],
            "FGA_RANK": [10, 5, 12, 65, 8],
            "FG_PCT_RANK": [12, 8, 15, 120, 10],
            "FG3M_RANK": [25, 55, 18, 12, 40],
            "FG3A_RANK": [30, 50, 22, 18, 45],
            "FG3_PCT_RANK": [55, 125, 45, 35, 65],
            "FTM_RANK": [15, 10, 25, 55, 5],
            "FTA_RANK": [18, 8, 22, 50, 5],
            "FT_PCT_RANK": [8, 125, 55, 25, 12],
            "OREB_RANK": [125, 15, 65, 45, 10],
            "DREB_RANK": [35, 5, 25, 40, 12],
            "REB_RANK": [40, 3, 22, 30, 8],
            "AST_RANK": [25, 18, 8, 120, 35],
            "TOV_RANK": [45, 35, 40, 85, 30],
            "STL_RANK": [55, 35, 25, 125, 40],
            "BLK_RANK": [25, 18, 55, 185, 12],
            "BLKA_RANK": [65, 45, 65, 125, 45],
            "PF_RANK": [85, 45, 95, 75, 35],
            "PFD_RANK": [25, 8, 40, 85, 5],
            "PTS_RANK": [3, 2, 5, 85, 1],
            "PLUS_MINUS_RANK": [18, 5, 25, 45, 12],
            "NBA_FANTASY_PTS_RANK": [5, 2, 8, 55, 3],
            "DD2_RANK": [25, 3, 12, 55, 5],
            "TD3_RANK": [25, 3, 10, 150, 18],
            "WNBA_FANTASY_PTS": [0.0] * 5,
        }
    )
    mock_response = MagicMock()
    mock_response.get_data_frames.return_value = [mock_df]
    mocker.patch(
        "nba_api.stats.endpoints.LeagueDashPlayerStats", return_value=mock_response
    )
    return mock_df


@pytest.fixture(autouse=True)
def mock_team_game_log(mocker):
    """Mock TeamGameLog API call."""
    today = datetime.now()
    dates = [(today - timedelta(days=i * 2)).strftime("%Y-%m-%d") for i in range(10)]

    mock_df = pd.DataFrame(
        {
            "Team_ID": [1610612749] * 10,
            "Game_ID": [f"002240060{i}" for i in range(10)],
            "GAME_DATE": dates,
            "MATCHUP": [
                "MIL vs. BOS",
                "MIL @ MIA",
                "MIL vs. DEN",
                "MIL @ PHX",
                "MIL vs. GSW",
            ]
            * 2,
            "WL": ["W", "L"] * 5,
            "W": [1, 0] * 5,
            "L": [0, 1] * 5,
            "W_PCT": [1.0, 0.0] * 5,
            "MIN": [240] * 10,
            "FGM": [42] * 10,
            "FGA": [88] * 10,
            "FG_PCT": [0.477] * 10,
            "FG3M": [12] * 10,
            "FG3A": [35] * 10,
            "FG3_PCT": [0.343] * 10,
            "FTM": [18] * 10,
            "FTA": [22] * 10,
            "FT_PCT": [0.818] * 10,
            "OREB": [10] * 10,
            "DREB": [35] * 10,
            "REB": [45] * 10,
            "AST": [25] * 10,
            "STL": [8] * 10,
            "BLK": [5] * 10,
            "TOV": [12] * 10,
            "PF": [20] * 10,
            "PTS": [114] * 10,
            "PLUS_MINUS": [8] * 10,
        }
    )
    mock_response = MagicMock()
    mock_response.get_data_frames.return_value = [mock_df]
    mocker.patch("nba_api.stats.endpoints.TeamGameLog", return_value=mock_response)
    return mock_df


@pytest.fixture(autouse=True)
def mock_league_game_log(mocker):
    """Mock LeagueGameLog API call for get_recent_games_summary."""
    today = datetime.now()
    dates = [(today - timedelta(days=i)).strftime("%Y-%m-%d") for i in range(5)]

    # Create game log with both home and away teams
    mock_df = pd.DataFrame(
        {
            "SEASON_ID": ["22024"] * 10,
            "TEAM_ID": [
                1610612749,
                1610612738,
                1610612747,
                1610612751,
                1610612744,
            ]
            * 2,
            "TEAM_ABBREVIATION": ["MIL", "BOS", "LAL", "BKN", "GSW"] * 2,
            "TEAM_NAME": [
                "Milwaukee Bucks",
                "Boston Celtics",
                "Los Angeles Lakers",
                "Brooklyn Nets",
                "Golden State Warriors",
            ]
            * 2,
            "GAME_ID": [
                "0022400500",
                "0022400500",
                "0022400501",
                "0022400501",
                "0022400502",
                "0022400502",
                "0022400503",
                "0022400503",
                "0022400504",
                "0022400504",
            ],
            "GAME_DATE": [dates[0]] * 2
            + [dates[1]] * 2
            + [dates[2]] * 2
            + [dates[3]] * 2
            + [dates[4]] * 2,
            "MATCHUP": [
                "MIL vs. BOS",
                "BOS @ MIL",
                "LAL vs. BKN",
                "BKN @ LAL",
                "GSW vs. MIL",
                "MIL @ GSW",
                "BOS vs. LAL",
                "LAL @ BOS",
                "BKN vs. GSW",
                "GSW @ BKN",
            ],
            "WL": ["W", "L", "W", "L", "L", "W", "W", "L", "L", "W"],
            "MIN": [240] * 10,
            "FGM": [42, 38, 45, 40, 38, 44, 41, 39, 36, 42],
            "FGA": [88, 85, 90, 88, 86, 89, 87, 85, 84, 88],
            "FG_PCT": [
                0.477,
                0.447,
                0.500,
                0.455,
                0.442,
                0.494,
                0.471,
                0.459,
                0.429,
                0.477,
            ],
            "FG3M": [12, 10, 14, 11, 9, 13, 11, 10, 8, 12],
            "FG3A": [35, 32, 38, 35, 33, 36, 34, 33, 30, 35],
            "FG3_PCT": [
                0.343,
                0.313,
                0.368,
                0.314,
                0.273,
                0.361,
                0.324,
                0.303,
                0.267,
                0.343,
            ],
            "FTM": [18, 15, 20, 16, 14, 19, 17, 15, 13, 18],
            "FTA": [22, 18, 24, 20, 17, 23, 21, 19, 16, 22],
            "FT_PCT": [
                0.818,
                0.833,
                0.833,
                0.800,
                0.824,
                0.826,
                0.810,
                0.789,
                0.813,
                0.818,
            ],
            "OREB": [10, 8, 12, 9, 7, 11, 9, 8, 6, 10],
            "DREB": [35, 32, 38, 34, 30, 37, 34, 32, 29, 35],
            "REB": [45, 40, 50, 43, 37, 48, 43, 40, 35, 45],
            "AST": [25, 22, 28, 24, 20, 27, 24, 22, 19, 25],
            "STL": [8, 6, 10, 7, 5, 9, 7, 6, 4, 8],
            "BLK": [5, 4, 6, 5, 3, 5, 4, 4, 3, 5],
            "TOV": [12, 14, 10, 13, 15, 11, 12, 14, 16, 12],
            "PF": [20, 22, 18, 21, 23, 19, 20, 22, 24, 20],
            "PTS": [114, 101, 124, 107, 99, 120, 110, 103, 93, 114],
            "PLUS_MINUS": [13, -13, 17, -17, -21, 21, 7, -7, -21, 21],
            "VIDEO_AVAILABLE": [1] * 10,
        }
    )
    mock_response = MagicMock()
    mock_response.get_data_frames.return_value = [mock_df]
    mocker.patch("nba_api.stats.endpoints.LeagueGameLog", return_value=mock_response)
    return mock_df


@pytest.fixture(autouse=True)
def mock_player_dashboard_by_year(mocker):
    """Mock PlayerDashboardByYearOverYear API call for career stats."""
    # First df is overall, second is by year
    mock_overall_df = pd.DataFrame(
        {
            "GROUP_SET": ["Overall"],
            "GROUP_VALUE": ["2024-25"],
            "GP": [50],
            "W": [30],
            "L": [20],
            "W_PCT": [0.600],
            "MIN": [35.5],
            "FGM": [9.8],
            "FGA": [18.0],
            "FG_PCT": [0.544],
            "FG3M": [2.5],
            "FG3A": [6.5],
            "FG3_PCT": [0.385],
            "FTM": [4.2],
            "FTA": [5.5],
            "FT_PCT": [0.764],
            "OREB": [1.0],
            "DREB": [7.0],
            "REB": [8.0],
            "AST": [8.5],
            "TOV": [3.2],
            "STL": [1.2],
            "BLK": [0.8],
            "BLKA": [0.5],
            "PF": [1.8],
            "PFD": [4.5],
            "PTS": [26.5],
            "PLUS_MINUS": [4.0],
        }
    )

    mock_by_year_df = pd.DataFrame(
        {
            "GROUP_SET": ["By Year"] * 5,
            "GROUP_VALUE": ["2024-25", "2023-24", "2022-23", "2021-22", "2020-21"],
            "TEAM_ID": [1610612747] * 5,
            "TEAM_ABBREVIATION": ["LAL"] * 5,
            "MAX_GAME_DATE": [
                "2025-01-15",
                "2024-04-15",
                "2023-04-10",
                "2022-04-08",
                "2021-05-15",
            ],
            "GP": [50, 71, 55, 56, 45],
            "W": [30, 42, 33, 33, 30],
            "L": [20, 29, 22, 23, 15],
            "W_PCT": [0.600, 0.592, 0.600, 0.589, 0.667],
            "MIN": [35.5, 35.3, 35.5, 37.2, 33.4],
            "FGM": [9.8, 9.0, 10.2, 10.8, 9.9],
            "FGA": [18.0, 17.2, 18.8, 19.5, 18.2],
            "FG_PCT": [0.544, 0.523, 0.543, 0.554, 0.544],
            "FG3M": [2.5, 2.1, 2.5, 2.9, 2.0],
            "FG3A": [6.5, 5.8, 6.8, 7.5, 5.5],
            "FG3_PCT": [0.385, 0.362, 0.368, 0.387, 0.364],
            "FTM": [4.2, 4.8, 5.2, 5.8, 5.5],
            "FTA": [5.5, 6.2, 6.8, 7.5, 7.0],
            "FT_PCT": [0.764, 0.774, 0.765, 0.773, 0.786],
            "OREB": [1.0, 0.8, 1.2, 1.1, 0.6],
            "DREB": [7.0, 6.5, 7.8, 7.2, 7.2],
            "REB": [8.0, 7.3, 9.0, 8.3, 7.8],
            "AST": [8.5, 8.3, 6.8, 6.2, 7.8],
            "TOV": [3.2, 3.5, 3.2, 3.5, 3.7],
            "STL": [1.2, 1.3, 0.9, 1.7, 1.1],
            "BLK": [0.8, 0.5, 0.6, 1.1, 0.6],
            "BLKA": [0.5, 0.6, 0.5, 0.5, 0.5],
            "PF": [1.8, 1.6, 1.8, 2.0, 1.6],
            "PFD": [4.5, 4.8, 5.0, 5.5, 5.2],
            "PTS": [26.5, 25.7, 28.9, 30.3, 25.0],
            "PLUS_MINUS": [4.0, 3.5, 4.8, 2.8, 5.5],
        }
    )

    mock_response = MagicMock()
    mock_response.get_data_frames.return_value = [mock_overall_df, mock_by_year_df]
    mocker.patch(
        "nba_api.stats.endpoints.PlayerDashboardByYearOverYear",
        return_value=mock_response,
    )
    return mock_by_year_df


@pytest.fixture(autouse=True)
def mock_synergy_play_types(mocker):
    """Mock SynergyPlayTypes API call for play type stats."""
    mock_df = pd.DataFrame(
        {
            "PLAYER_ID": [201566, 203507, 2544],
            "PLAYER_NAME": ["Kevin Durant", "Giannis Antetokounmpo", "LeBron James"],
            "TEAM_ID": [1610612756, 1610612749, 1610612747],
            "TEAM_ABBREVIATION": ["PHX", "MIL", "LAL"],
            "TEAM_NAME": ["Phoenix Suns", "Milwaukee Bucks", "Los Angeles Lakers"],
            "PLAY_TYPE": ["Isolation", "Isolation", "Isolation"],
            "TYPE_GROUPING": ["Offensive", "Offensive", "Offensive"],
            "PERCENTILE": [0.95, 0.92, 0.88],
            "GP": [50, 52, 48],
            "POSS_PCT": [0.18, 0.15, 0.12],
            "PPP": [1.15, 1.22, 1.08],
            "FG_PCT": [0.48, 0.52, 0.45],
            "FT_FREQ": [0.12, 0.18, 0.10],
            "TOV_FREQ": [0.08, 0.10, 0.07],
            "SF_FREQ": [0.15, 0.22, 0.12],
            "PLUSONE_FREQ": [0.05, 0.08, 0.04],
            "SCORE_FREQ": [0.52, 0.58, 0.48],
            "EFG_PCT": [0.52, 0.55, 0.48],
            "POSS": [150, 160, 120],
            "PTS": [172, 195, 130],
            "FGM": [72, 83, 54],
            "FGA": [150, 160, 120],
            "FGMX": [78, 77, 66],
        }
    )
    mock_response = MagicMock()
    mock_response.get_data_frames.return_value = [mock_df]
    mocker.patch("nba_api.stats.endpoints.SynergyPlayTypes", return_value=mock_response)
    return mock_df


@pytest.fixture(autouse=True)
def mock_league_dash_pt_stats(mocker):
    """Mock LeagueDashPtStats API call for tracking stats."""
    mock_df = pd.DataFrame(
        {
            "PLAYER_ID": [201566, 203507, 2544],
            "PLAYER_NAME": ["Kevin Durant", "Giannis Antetokounmpo", "LeBron James"],
            "TEAM_ID": [1610612756, 1610612749, 1610612747],
            "TEAM_ABBREVIATION": ["PHX", "MIL", "LAL"],
            "TEAM_NAME": ["Phoenix Suns", "Milwaukee Bucks", "Los Angeles Lakers"],
            "AGE": [35, 29, 39],
            "GP": [50, 52, 48],
            "W": [30, 35, 28],
            "L": [20, 17, 20],
            "MIN": [35.5, 32.8, 35.2],
            "DIST_FEET": [14500, 15200, 14800],
            "DIST_MILES": [2.75, 2.88, 2.80],
            "DIST_MILES_OFF": [1.35, 1.42, 1.38],
            "DIST_MILES_DEF": [1.40, 1.46, 1.42],
            "AVG_SPEED": [4.2, 4.5, 4.3],
            "AVG_SPEED_OFF": [4.5, 4.8, 4.6],
            "AVG_SPEED_DEF": [3.9, 4.2, 4.0],
        }
    )
    mock_response = MagicMock()
    mock_response.get_data_frames.return_value = [mock_df]
    mocker.patch(
        "nba_api.stats.endpoints.LeagueDashPtStats", return_value=mock_response
    )
    return mock_df


@pytest.fixture(autouse=True)
def mock_common_player_info(mocker):
    """Mock CommonPlayerInfo API call for player info."""
    mock_df = pd.DataFrame(
        {
            "PERSON_ID": [2544],
            "FIRST_NAME": ["LeBron"],
            "LAST_NAME": ["James"],
            "DISPLAY_FIRST_LAST": ["LeBron James"],
            "DISPLAY_LAST_COMMA_FIRST": ["James, LeBron"],
            "DISPLAY_FI_LAST": ["L. James"],
            "PLAYER_SLUG": ["lebron-james"],
            "BIRTHDATE": ["1984-12-30T00:00:00"],
            "SCHOOL": ["St. Vincent-St. Mary HS (OH)"],
            "COUNTRY": ["USA"],
            "LAST_AFFILIATION": ["St. Vincent-St. Mary HS (OH)/USA"],
            "HEIGHT": ["6-9"],
            "WEIGHT": ["250"],
            "SEASON_EXP": [21],
            "JERSEY": ["23"],
            "POSITION": ["Forward"],
            "ROSTERSTATUS": ["Active"],
            "GAMES_PLAYED_CURRENT_SEASON_FLAG": ["Y"],
            "TEAM_ID": [1610612747],
            "TEAM_NAME": ["Los Angeles Lakers"],
            "TEAM_ABBREVIATION": ["LAL"],
            "TEAM_CODE": ["lakers"],
            "TEAM_CITY": ["Los Angeles"],
            "PLAYERCODE": ["lebron_james"],
            "FROM_YEAR": [2003],
            "TO_YEAR": [2024],
            "DLEAGUE_FLAG": ["N"],
            "NBA_FLAG": ["Y"],
            "GAMES_PLAYED_FLAG": ["Y"],
            "DRAFT_YEAR": ["2003"],
            "DRAFT_ROUND": ["1"],
            "DRAFT_NUMBER": ["1"],
            "GREATEST_75_FLAG": ["Y"],
        }
    )
    mock_response = MagicMock()
    mock_response.get_data_frames.return_value = [mock_df]
    mocker.patch("nba_api.stats.endpoints.CommonPlayerInfo", return_value=mock_response)
    return mock_df


@pytest.fixture(autouse=True)
def mock_common_team_roster(mocker):
    """Mock CommonTeamRoster API call for team roster."""
    mock_df = pd.DataFrame(
        {
            "TeamID": [1610612747] * 3,
            "SEASON": ["2024-25"] * 3,
            "LeagueID": ["00"] * 3,
            "PLAYER": ["LeBron James", "Anthony Davis", "Austin Reaves"],
            "NICKNAME": ["LeBron", "AD", "Hillbilly Kobe"],
            "PLAYER_SLUG": ["lebron-james", "anthony-davis", "austin-reaves"],
            "NUM": ["23", "3", "15"],
            "POSITION": ["F", "F-C", "G"],
            "HEIGHT": ["6-9", "6-10", "6-5"],
            "WEIGHT": ["250", "253", "197"],
            "BIRTH_DATE": ["DEC 30, 1984", "MAR 11, 1993", "MAY 29, 1998"],
            "AGE": [40, 31, 26],
            "EXP": ["21", "12", "3"],
            "SCHOOL": [
                "St. Vincent-St. Mary HS (OH)",
                "Kentucky",
                "Oklahoma",
            ],
            "PLAYER_ID": [2544, 203076, 1630559],
            "HOW_ACQUIRED": ["Signed"] * 3,
        }
    )
    mock_coaches_df = pd.DataFrame(
        {
            "TEAM_ID": [1610612747],
            "SEASON": ["2024-25"],
            "COACH_ID": ["204091"],
            "FIRST_NAME": ["JJ"],
            "LAST_NAME": ["Redick"],
            "COACH_NAME": ["JJ Redick"],
            "IS_ASSISTANT": [0],
            "COACH_TYPE": ["Head Coach"],
            "SCHOOL": ["Duke"],
        }
    )
    mock_response = MagicMock()
    mock_response.get_data_frames.return_value = [mock_df, mock_coaches_df]
    mocker.patch("nba_api.stats.endpoints.CommonTeamRoster", return_value=mock_response)
    return mock_df


@pytest.fixture(autouse=True)
def mock_boxscore_traditional_v3(mocker):
    """Mock BoxScoreTraditionalV3 API call for game boxscore."""
    mock_player_df = pd.DataFrame(
        {
            "gameId": ["0022301148"] * 4,
            "teamId": [1610612747, 1610612747, 1610612738, 1610612738],
            "teamCity": ["Los Angeles", "Los Angeles", "Boston", "Boston"],
            "teamName": ["Lakers", "Lakers", "Celtics", "Celtics"],
            "teamTricode": ["LAL", "LAL", "BOS", "BOS"],
            "personId": [2544, 203076, 1628369, 203935],
            "firstName": ["LeBron", "Anthony", "Jayson", "Marcus"],
            "familyName": ["James", "Davis", "Tatum", "Smart"],
            "nameI": ["L. James", "A. Davis", "J. Tatum", "M. Smart"],
            "position": ["F", "F-C", "F-G", "G"],
            "comment": [""] * 4,
            "jerseyNum": ["23", "3", "0", "36"],
            "minutes": ["PT35M22S", "PT36M15S", "PT38M10S", "PT34M45S"],
            "fieldGoalsMade": [10, 12, 11, 5],
            "fieldGoalsAttempted": [18, 20, 22, 12],
            "fieldGoalsPercentage": [0.556, 0.600, 0.500, 0.417],
            "threePointersMade": [2, 1, 4, 2],
            "threePointersAttempted": [5, 3, 10, 6],
            "threePointersPercentage": [0.400, 0.333, 0.400, 0.333],
            "freeThrowsMade": [6, 8, 5, 3],
            "freeThrowsAttempted": [8, 10, 6, 4],
            "freeThrowsPercentage": [0.750, 0.800, 0.833, 0.750],
            "reboundsOffensive": [1, 3, 1, 0],
            "reboundsDefensive": [7, 9, 5, 3],
            "reboundsTotal": [8, 12, 6, 3],
            "assists": [9, 3, 5, 8],
            "steals": [2, 1, 1, 2],
            "blocks": [1, 3, 1, 0],
            "turnovers": [3, 2, 2, 3],
            "foulsPersonal": [2, 4, 3, 4],
            "points": [28, 33, 31, 15],
            "plusMinusPoints": [12, 8, -5, -8],
        }
    )
    mock_team_df = pd.DataFrame(
        {
            "gameId": ["0022301148", "0022301148"],
            "teamId": [1610612747, 1610612738],
            "teamCity": ["Los Angeles", "Boston"],
            "teamName": ["Lakers", "Celtics"],
            "teamTricode": ["LAL", "BOS"],
            "fieldGoalsMade": [42, 40],
            "fieldGoalsAttempted": [88, 90],
            "fieldGoalsPercentage": [0.477, 0.444],
            "threePointersMade": [12, 14],
            "threePointersAttempted": [32, 38],
            "threePointersPercentage": [0.375, 0.368],
            "freeThrowsMade": [18, 16],
            "freeThrowsAttempted": [22, 20],
            "freeThrowsPercentage": [0.818, 0.800],
            "reboundsOffensive": [10, 8],
            "reboundsDefensive": [35, 32],
            "reboundsTotal": [45, 40],
            "assists": [25, 22],
            "steals": [8, 6],
            "blocks": [5, 4],
            "turnovers": [12, 14],
            "foulsPersonal": [20, 22],
            "points": [114, 110],
        }
    )
    mock_response = MagicMock()
    mock_response.get_data_frames.return_value = [mock_player_df, mock_team_df]
    mocker.patch(
        "nba_api.stats.endpoints.BoxScoreTraditionalV3", return_value=mock_response
    )
    return mock_player_df


@pytest.fixture(autouse=True)
def mock_boxscore_advanced_v3(mocker):
    """Mock BoxScoreAdvancedV3 API call for advanced boxscore."""
    mock_player_df = pd.DataFrame(
        {
            "gameId": ["0022301148"] * 2,
            "teamId": [1610612747, 1610612738],
            "personId": [2544, 1628369],
            "firstName": ["LeBron", "Jayson"],
            "familyName": ["James", "Tatum"],
            "offensiveRating": [118.5, 112.2],
            "defensiveRating": [105.2, 108.8],
            "netRating": [13.3, 3.4],
            "assistPercentage": [0.35, 0.22],
            "assistRatio": [28.5, 18.2],
            "assistToTurnover": [3.0, 2.5],
            "reboundPercentage": [0.12, 0.08],
            "trueShootingPercentage": [0.65, 0.58],
            "effectiveFieldGoalPercentage": [0.61, 0.55],
            "PIE": [0.22, 0.18],
        }
    )
    mock_team_df = pd.DataFrame(
        {
            "gameId": ["0022301148", "0022301148"],
            "teamId": [1610612747, 1610612738],
            "teamName": ["Lakers", "Celtics"],
            "offensiveRating": [115.0, 108.5],
            "defensiveRating": [108.5, 115.0],
            "netRating": [6.5, -6.5],
            "trueShootingPercentage": [0.58, 0.54],
            "PIE": [0.55, 0.45],
        }
    )
    mock_response = MagicMock()
    mock_response.get_data_frames.return_value = [mock_player_df, mock_team_df]
    mocker.patch(
        "nba_api.stats.endpoints.BoxScoreAdvancedV3", return_value=mock_response
    )
    return mock_player_df


@pytest.fixture(autouse=True)
def mock_playbyplay_v3(mocker):
    """Mock PlayByPlayV3 API call for play-by-play data."""
    mock_df = pd.DataFrame(
        {
            "gameId": ["0022301148"] * 5,
            "actionNumber": [1, 2, 3, 4, 5],
            "clock": ["PT12M00S", "PT11M45S", "PT11M30S", "PT11M15S", "PT11M00S"],
            "period": [1, 1, 1, 1, 1],
            "teamId": [1610612747, 1610612738, 1610612747, 0, 1610612738],
            "teamTricode": ["LAL", "BOS", "LAL", "", "BOS"],
            "personId": [2544, 1628369, 203076, 0, 203935],
            "playerName": [
                "LeBron James",
                "Jayson Tatum",
                "Anthony Davis",
                "",
                "Marcus Smart",
            ],
            "playerNameI": ["L. James", "J. Tatum", "A. Davis", "", "M. Smart"],
            "xLegacy": [0, 50, -100, 0, 150],
            "yLegacy": [0, 100, 50, 0, 200],
            "shotDistance": [0, 15, 8, 0, 22],
            "shotResult": ["", "Missed", "Made", "", "Made"],
            "isFieldGoal": [0, 1, 1, 0, 1],
            "scoreHome": ["0", "0", "2", "2", "2"],
            "scoreAway": ["0", "0", "0", "0", "3"],
            "pointsTotal": [0, 0, 2, 0, 3],
            "location": ["h", "h", "h", "h", "h"],
            "description": [
                "Jump Ball",
                "MISS Tatum 15' Pullup Jump Shot",
                "Davis 8' Driving Layup",
                "Timeout",
                "Smart 22' 3PT",
            ],
            "actionType": ["jumpball", "2pt", "2pt", "timeout", "3pt"],
            "subType": ["", "pullupjumpshot", "drivinglayup", "", ""],
        }
    )
    mock_response = MagicMock()
    mock_response.get_data_frames.return_value = [mock_df]
    mocker.patch("nba_api.stats.endpoints.PlayByPlayV3", return_value=mock_response)
    return mock_df


@pytest.fixture(autouse=True)
def mock_league_dash_team_stats(mocker):
    """Mock LeagueDashTeamStats API call for league team stats."""
    mock_df = pd.DataFrame(
        {
            "TEAM_ID": [1610612749, 1610612738, 1610612747],
            "TEAM_NAME": ["Milwaukee Bucks", "Boston Celtics", "Los Angeles Lakers"],
            "TEAM_ABBREVIATION": ["MIL", "BOS", "LAL"],
            "GP": [45, 46, 44],
            "W": [30, 32, 25],
            "L": [15, 14, 19],
            "W_PCT": [0.667, 0.696, 0.568],
            "MIN": [48.0, 48.0, 48.0],
            "FGM": [42.5, 44.2, 41.8],
            "FGA": [90.2, 88.5, 89.8],
            "FG_PCT": [0.471, 0.499, 0.465],
            "FG3M": [13.5, 16.2, 12.8],
            "FG3A": [38.2, 42.5, 36.5],
            "FG3_PCT": [0.354, 0.381, 0.351],
            "FTM": [18.5, 17.2, 19.8],
            "FTA": [23.2, 21.5, 25.0],
            "FT_PCT": [0.797, 0.800, 0.792],
            "OREB": [10.5, 9.2, 11.0],
            "DREB": [34.5, 36.2, 33.8],
            "REB": [45.0, 45.4, 44.8],
            "AST": [26.5, 28.2, 25.5],
            "TOV": [13.5, 12.8, 14.2],
            "STL": [7.5, 8.2, 7.0],
            "BLK": [5.5, 5.0, 4.8],
            "BLKA": [4.5, 4.2, 5.0],
            "PF": [19.5, 18.8, 20.2],
            "PFD": [20.2, 19.5, 21.0],
            "PTS": [117.0, 121.8, 116.2],
            "PLUS_MINUS": [5.5, 8.2, 3.5],
        }
    )
    mock_response = MagicMock()
    mock_response.get_data_frames.return_value = [mock_df]
    mocker.patch(
        "nba_api.stats.endpoints.LeagueDashTeamStats", return_value=mock_response
    )
    return mock_df
