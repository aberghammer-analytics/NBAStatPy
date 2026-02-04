"""Tests for NBAStatPy MCP tools using FastMCP in-memory testing.

Reduced test suite for reliable CI. Each tool has one basic happy path test,
with error handling consolidated into parametrized tests.

All external API calls are mocked via conftest.py fixtures to prevent timeouts
and ensure reliable testing.
"""

import pytest
from fastmcp.client import Client
from fastmcp.client.transports import FastMCPTransport
from loguru import logger

from nbastatpy.mcp.server import mcp


@pytest.fixture
async def mcp_client():
    """Fixture providing FastMCP client for in-memory testing."""
    async with Client(transport=mcp) as client:
        yield client


# ============================================================================
# Tool Registration Test
# ============================================================================


async def test_list_tools(mcp_client: Client[FastMCPTransport]):
    """Test that MCP server has registered tools."""
    tools = await mcp_client.list_tools()
    assert len(tools) >= 1

    tool_names = [tool.name for tool in tools]
    assert "get_player_game_logs" in tool_names
    assert "get_league_leaders" in tool_names
    assert "get_team_recent_games" in tool_names
    assert "get_recent_games_summary" in tool_names
    assert "get_recent_games_player_stats" in tool_names
    assert "get_player_career_stats" in tool_names
    assert "get_player_play_type_stats" in tool_names
    assert "get_player_tracking_stats" in tool_names
    assert "get_team_play_type_stats" in tool_names
    assert "get_team_tracking_stats" in tool_names
    assert "get_live_games" in tool_names


# ============================================================================
# Basic Happy Path Tests (one per tool)
# ============================================================================


async def test_get_league_leaders(mcp_client: Client[FastMCPTransport]):
    """Test league leaders for points."""
    result = await mcp_client.call_tool(
        name="get_league_leaders", arguments={"stat_category": "PTS", "limit": 10}
    )

    logger.info("League leaders (PTS) result:")
    logger.info(result.content[0].text)

    assert result.is_error is False
    assert len(result.content) > 0


async def test_get_team_recent_games(mcp_client: Client[FastMCPTransport]):
    """Test get_team_recent_games tool with basic usage."""
    result = await mcp_client.call_tool(
        name="get_team_recent_games",
        arguments={"team_abbreviation": "MIL", "last_n_games": 5},
    )

    logger.info("Team recent games result:")
    logger.info(result.content[0].text)

    assert result.is_error is False
    assert len(result.content) > 0

    data_text = result.content[0].text
    assert "pts" in data_text.lower() or "PTS" in data_text


async def test_get_player_game_logs(mcp_client: Client[FastMCPTransport]):
    """Test get_player_game_logs tool with basic usage."""
    result = await mcp_client.call_tool(
        name="get_player_game_logs",
        arguments={"player_name": "LeBron James", "last_n_games": 5},
    )

    logger.info("Player game logs result:")
    logger.info(result.content[0].text)

    assert result.is_error is False
    assert len(result.content) > 0

    data_text = result.content[0].text
    assert "pts" in data_text.lower() or "PTS" in data_text


async def test_get_recent_games_summary(mcp_client: Client[FastMCPTransport]):
    """Test get_recent_games_summary with default parameters."""
    result = await mcp_client.call_tool(
        name="get_recent_games_summary", arguments={"last_n_days": 7}
    )

    logger.info("Recent games summary result:")
    logger.info(result.content[0].text)

    assert result.is_error is False
    assert len(result.content) > 0


async def test_get_recent_games_player_stats(mcp_client: Client[FastMCPTransport]):
    """Test get_recent_games_player_stats with default parameters."""
    result = await mcp_client.call_tool(
        name="get_recent_games_player_stats", arguments={"last_n_days": 7}
    )

    logger.info("Recent games player stats result:")
    logger.info(result.content[0].text)

    assert result.is_error is False
    assert len(result.content) > 0


async def test_get_player_career_stats(mcp_client: Client[FastMCPTransport]):
    """Test get_player_career_stats with default parameters."""
    result = await mcp_client.call_tool(
        name="get_player_career_stats", arguments={"player_name": "Stephen Curry"}
    )

    logger.info("Player career stats result:")
    logger.info(result.content[0].text)

    assert result.is_error is False
    assert len(result.content) > 0

    data_text = result.content[0].text
    assert "pts" in data_text.lower() or "PTS" in data_text


async def test_get_player_play_type_stats(mcp_client: Client[FastMCPTransport]):
    """Test get_player_play_type_stats for isolation plays."""
    result = await mcp_client.call_tool(
        name="get_player_play_type_stats", arguments={"play_type": "Isolation"}
    )

    logger.info("Player isolation stats result:")
    logger.info(result.content[0].text[:500])

    assert result.is_error is False
    assert len(result.content) > 0


async def test_get_player_tracking_stats(mcp_client: Client[FastMCPTransport]):
    """Test get_player_tracking_stats for speed and distance."""
    result = await mcp_client.call_tool(
        name="get_player_tracking_stats", arguments={"track_type": "SpeedDistance"}
    )

    logger.info("Player speed/distance stats result:")
    logger.info(result.content[0].text[:500])

    assert result.is_error is False
    assert len(result.content) > 0


async def test_get_team_play_type_stats(mcp_client: Client[FastMCPTransport]):
    """Test get_team_play_type_stats for transition plays."""
    result = await mcp_client.call_tool(
        name="get_team_play_type_stats", arguments={"play_type": "Transition"}
    )

    logger.info("Team transition stats result:")
    logger.info(result.content[0].text[:500])

    assert result.is_error is False
    assert len(result.content) > 0


async def test_get_team_tracking_stats(mcp_client: Client[FastMCPTransport]):
    """Test get_team_tracking_stats for passing statistics."""
    result = await mcp_client.call_tool(
        name="get_team_tracking_stats", arguments={"track_type": "Passing"}
    )

    logger.info("Team passing stats result:")
    logger.info(result.content[0].text[:500])

    assert result.is_error is False
    assert len(result.content) > 0


# ============================================================================
# Consolidated Error Handling Tests
# ============================================================================


async def test_get_player_game_logs_invalid_player(
    mcp_client: Client[FastMCPTransport],
):
    """Test error handling for non-existent player."""
    result = await mcp_client.call_tool(
        name="get_player_game_logs",
        arguments={"player_name": "Invalid Player Name XYZ"},
        raise_on_error=False,
    )

    logger.info("Invalid player error:")
    logger.info(result.content[0].text)

    assert result.is_error is True
    assert "not found" in result.content[0].text


async def test_get_player_game_logs_invalid_last_n_games(
    mcp_client: Client[FastMCPTransport],
):
    """Test error handling for invalid last_n_games value."""
    result = await mcp_client.call_tool(
        name="get_player_game_logs",
        arguments={"player_name": "LeBron James", "last_n_games": 0},
        raise_on_error=False,
    )

    logger.info("Invalid last_n_games error:")
    logger.info(result.content[0].text)

    assert result.is_error is True
    assert "last_n_games must be between 1 and 82" in result.content[0].text


async def test_get_recent_games_summary_invalid_days(
    mcp_client: Client[FastMCPTransport],
):
    """Test error handling for invalid last_n_days value."""
    result = await mcp_client.call_tool(
        name="get_recent_games_summary",
        arguments={"last_n_days": 0},
        raise_on_error=False,
    )

    logger.info("Invalid last_n_days error:")
    logger.info(result.content[0].text)

    assert result.is_error is True
    assert "last_n_days must be between 1 and 365" in result.content[0].text


async def test_get_player_career_stats_invalid_player(
    mcp_client: Client[FastMCPTransport],
):
    """Test error handling for non-existent player in career stats."""
    result = await mcp_client.call_tool(
        name="get_player_career_stats",
        arguments={"player_name": "Invalid Player Name XYZ"},
        raise_on_error=False,
    )

    logger.info("Invalid player error:")
    logger.info(result.content[0].text)

    assert result.is_error is True
    assert "not found" in result.content[0].text


# ============================================================================
# Validation Tests for Validators class
# ============================================================================


async def test_get_team_recent_games_invalid_team(
    mcp_client: Client[FastMCPTransport],
):
    """Test error handling for invalid team abbreviation."""
    result = await mcp_client.call_tool(
        name="get_team_recent_games",
        arguments={"team_abbreviation": "XXX", "last_n_games": 5},
        raise_on_error=False,
    )

    logger.info("Invalid team abbreviation error:")
    logger.info(result.content[0].text)

    assert result.is_error is True
    assert "Invalid team abbreviation" in result.content[0].text


async def test_get_team_recent_games_invalid_season_type(
    mcp_client: Client[FastMCPTransport],
):
    """Test error handling for invalid season_type."""
    result = await mcp_client.call_tool(
        name="get_team_recent_games",
        arguments={
            "team_abbreviation": "LAL",
            "last_n_games": 5,
            "season_type": "Invalid Season Type",
        },
        raise_on_error=False,
    )

    logger.info("Invalid season_type error:")
    logger.info(result.content[0].text)

    assert result.is_error is True
    assert "Invalid season_type" in result.content[0].text


async def test_get_player_game_logs_negative_last_n_games(
    mcp_client: Client[FastMCPTransport],
):
    """Test error handling for negative last_n_games value."""
    result = await mcp_client.call_tool(
        name="get_player_game_logs",
        arguments={"player_name": "LeBron James", "last_n_games": -1},
        raise_on_error=False,
    )

    logger.info("Negative last_n_games error:")
    logger.info(result.content[0].text)

    assert result.is_error is True
    assert "last_n_games must be between 1 and 82" in result.content[0].text


async def test_get_player_game_logs_exceeds_max_games(
    mcp_client: Client[FastMCPTransport],
):
    """Test error handling for last_n_games exceeding max (82)."""
    result = await mcp_client.call_tool(
        name="get_player_game_logs",
        arguments={"player_name": "LeBron James", "last_n_games": 83},
        raise_on_error=False,
    )

    logger.info("Exceeds max last_n_games error:")
    logger.info(result.content[0].text)

    assert result.is_error is True
    assert "last_n_games must be between 1 and 82" in result.content[0].text


async def test_get_recent_games_summary_negative_days(
    mcp_client: Client[FastMCPTransport],
):
    """Test error handling for negative last_n_days value."""
    result = await mcp_client.call_tool(
        name="get_recent_games_summary",
        arguments={"last_n_days": -5},
        raise_on_error=False,
    )

    logger.info("Negative last_n_days error:")
    logger.info(result.content[0].text)

    assert result.is_error is True
    assert "last_n_days must be between 1 and 365" in result.content[0].text


async def test_get_league_leaders_invalid_limit(
    mcp_client: Client[FastMCPTransport],
):
    """Test error handling for invalid limit value in league leaders."""
    result = await mcp_client.call_tool(
        name="get_league_leaders",
        arguments={"stat_category": "PTS", "limit": 0},
        raise_on_error=False,
    )

    logger.info("Invalid limit error:")
    logger.info(result.content[0].text)

    assert result.is_error is True
    assert "limit must be between" in result.content[0].text


# ============================================================================
# Tests for New Tools
# ============================================================================


async def test_list_new_tools(mcp_client: Client[FastMCPTransport]):
    """Test that new MCP tools are registered."""
    tools = await mcp_client.list_tools()
    tool_names = [tool.name for tool in tools]

    # New tools added in Phase 5
    assert "get_player_info" in tool_names
    assert "get_team_roster" in tool_names
    assert "get_game_boxscore" in tool_names
    assert "get_game_playbyplay" in tool_names
    assert "get_league_player_stats" in tool_names
    assert "get_league_team_stats" in tool_names


async def test_get_player_info(mcp_client: Client[FastMCPTransport]):
    """Test get_player_info tool with basic usage."""
    result = await mcp_client.call_tool(
        name="get_player_info", arguments={"player_name": "LeBron James"}
    )

    logger.info("Player info result:")
    logger.info(result.content[0].text[:500])

    assert result.is_error is False
    assert len(result.content) > 0

    data_text = result.content[0].text
    assert "player_id" in data_text.lower() or "LeBron" in data_text


async def test_get_team_roster(mcp_client: Client[FastMCPTransport]):
    """Test get_team_roster tool with basic usage."""
    result = await mcp_client.call_tool(
        name="get_team_roster", arguments={"team_abbreviation": "LAL"}
    )

    logger.info("Team roster result:")
    logger.info(result.content[0].text[:500])

    assert result.is_error is False
    assert len(result.content) > 0


async def test_get_team_roster_invalid_team(mcp_client: Client[FastMCPTransport]):
    """Test get_team_roster with invalid team abbreviation."""
    result = await mcp_client.call_tool(
        name="get_team_roster",
        arguments={"team_abbreviation": "INVALID"},
        raise_on_error=False,
    )

    logger.info("Invalid team roster error:")
    logger.info(result.content[0].text)

    assert result.is_error is True
    assert "Invalid team abbreviation" in result.content[0].text


async def test_get_game_boxscore(mcp_client: Client[FastMCPTransport]):
    """Test get_game_boxscore tool with basic usage."""
    result = await mcp_client.call_tool(
        name="get_game_boxscore", arguments={"game_id": "0022301148"}
    )

    logger.info("Game boxscore result:")
    logger.info(result.content[0].text[:500])

    assert result.is_error is False
    assert len(result.content) > 0


async def test_get_game_playbyplay(mcp_client: Client[FastMCPTransport]):
    """Test get_game_playbyplay tool with basic usage."""
    result = await mcp_client.call_tool(
        name="get_game_playbyplay", arguments={"game_id": "0022301148"}
    )

    logger.info("Game play-by-play result:")
    logger.info(result.content[0].text[:500])

    assert result.is_error is False
    assert len(result.content) > 0


async def test_get_league_player_stats(mcp_client: Client[FastMCPTransport]):
    """Test get_league_player_stats tool with basic usage."""
    result = await mcp_client.call_tool(
        name="get_league_player_stats", arguments={"limit": 10}
    )

    logger.info("League player stats result:")
    logger.info(result.content[0].text[:500])

    assert result.is_error is False
    assert len(result.content) > 0


async def test_get_league_team_stats(mcp_client: Client[FastMCPTransport]):
    """Test get_league_team_stats tool with basic usage."""
    result = await mcp_client.call_tool(name="get_league_team_stats", arguments={})

    logger.info("League team stats result:")
    logger.info(result.content[0].text[:500])

    assert result.is_error is False
    assert len(result.content) > 0


async def test_get_live_games(mcp_client: Client[FastMCPTransport]):
    """Test get_live_games tool with basic usage (uses mock data)."""
    import json

    result = await mcp_client.call_tool(name="get_live_games", arguments={})

    logger.info("Live games result:")
    logger.info(result.content[0].text[:500])

    assert result.is_error is False
    assert len(result.content) > 0

    # Parse result and verify it matches mock data
    games = json.loads(result.content[0].text)
    assert len(games) == 2  # Mock has 2 games

    # Verify first game matches mock (CHI vs LAC)
    assert games[0]["game_id"] == "0022400500"
    assert games[0]["home_team"]["abbreviation"] == "CHI"
    assert games[0]["away_team"]["abbreviation"] == "LAC"
    assert games[0]["home_team"]["score"] == 84
    assert games[0]["game_leaders"]["home"]["name"] == "Nikola Vucevic"


async def test_get_live_games_with_team_filter(mcp_client: Client[FastMCPTransport]):
    """Test get_live_games tool with team filter (uses mock data)."""
    import json

    result = await mcp_client.call_tool(
        name="get_live_games", arguments={"team_abbreviation": "LAL"}
    )

    logger.info("Live games for LAL:")
    logger.info(result.content[0].text[:500])

    assert result.is_error is False
    assert len(result.content) > 0

    # Parse result and verify filter works with mock data
    games = json.loads(result.content[0].text)
    assert len(games) == 1  # Mock has 1 LAL game (LAL vs BOS)
    assert games[0]["game_id"] == "0022400501"
    assert games[0]["home_team"]["abbreviation"] == "LAL"
    assert games[0]["away_team"]["abbreviation"] == "BOS"
