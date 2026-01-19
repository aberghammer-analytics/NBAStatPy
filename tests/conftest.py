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
