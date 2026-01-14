"""Tests for NBAStatPy MCP tools using FastMCP in-memory testing."""

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


async def test_list_tools(mcp_client: Client[FastMCPTransport]):
    """Test that MCP server has registered tools."""
    tools = await mcp_client.list_tools()
    assert len(tools) >= 1

    tool_names = [tool.name for tool in tools]
    assert "get_player_salary" in tool_names
    assert "get_player_game_logs" in tool_names


async def test_get_player_salary(mcp_client: Client[FastMCPTransport]):
    """Test get_player_salary tool with basic usage."""
    result = await mcp_client.call_tool(
        name="get_player_salary",
        arguments={"player_name": "LeBron James"}
    )

    # Log the tool output
    logger.info("Tool call result:")
    logger.info(result.content[0].text)

    assert result.is_error is False
    assert len(result.content) > 0

    # Verify data contains expected information
    data_text = result.content[0].text
    assert "season" in data_text.lower() or "2" in data_text
    assert any(keyword in data_text.lower() for keyword in ["salary", "$", "million"])


async def test_get_league_leaders_points(mcp_client: Client[FastMCPTransport]):
    """Test league leaders for points."""
    result = await mcp_client.call_tool(
        name="get_league_leaders",
        arguments={"stat_category": "PTS", "limit": 10}
    )

    logger.info("League leaders (PTS) result:")
    logger.info(result.content[0].text)

    assert result.is_error is False
    assert len(result.content) > 0


async def test_get_league_leaders_alltime(mcp_client: Client[FastMCPTransport]):
    """Test all-time career leaders."""
    result = await mcp_client.call_tool(
        name="get_league_leaders",
        arguments={"stat_category": "points", "season": "all-time", "limit": 5}
    )

    logger.info("All-time leaders result:")
    logger.info(result.content[0].text)

    assert result.is_error is False
    assert len(result.content) > 0


async def test_get_league_leaders_specific_season(mcp_client: Client[FastMCPTransport]):
    """Test leaders for a specific season."""
    result = await mcp_client.call_tool(
        name="get_league_leaders",
        arguments={"stat_category": "rebounds", "season": "2023-24"}
    )

    logger.info("2023-24 rebounding leaders result:")
    logger.info(result.content[0].text)

    assert result.is_error is False
    assert len(result.content) > 0


async def test_get_team_recent_games_basic(mcp_client: Client[FastMCPTransport]):
    """Test get_team_recent_games tool with basic usage."""
    result = await mcp_client.call_tool(
        name="get_team_recent_games",
        arguments={"team_abbreviation": "MIL", "last_n_games": 5}
    )

    logger.info("Team recent games result:")
    logger.info(result.content[0].text)

    assert result.is_error is False
    assert len(result.content) > 0

    # Verify data contains expected information
    data_text = result.content[0].text
    assert "pts" in data_text.lower() or "PTS" in data_text


async def test_get_team_recent_games_with_opponent_stats(mcp_client: Client[FastMCPTransport]):
    """Test get_team_recent_games with opponent stats included."""
    result = await mcp_client.call_tool(
        name="get_team_recent_games",
        arguments={
            "team_abbreviation": "LAL",
            "last_n_games": 3,
            "include_opponent_stats": True,
        }
    )

    logger.info("Team recent games with opponent stats:")
    logger.info(result.content[0].text)

    assert result.is_error is False
    assert len(result.content) > 0

    # Verify opponent stats are included
    data_text = result.content[0].text
    assert "opp_pts" in data_text.lower() or "OPP_PTS" in data_text


async def test_get_team_recent_games_specific_season(mcp_client: Client[FastMCPTransport]):
    """Test get_team_recent_games with specific season."""
    result = await mcp_client.call_tool(
        name="get_team_recent_games",
        arguments={
            "team_abbreviation": "BOS",
            "last_n_games": 5,
            "season": "2023-24",
        }
    )

    logger.info("Team recent games for 2023-24 season:")
    logger.info(result.content[0].text)

    assert result.is_error is False
    assert len(result.content) > 0


async def test_get_player_game_logs_basic(mcp_client: Client[FastMCPTransport]):
    """Test get_player_game_logs tool with basic usage."""
    result = await mcp_client.call_tool(
        name="get_player_game_logs",
        arguments={"player_name": "LeBron James", "last_n_games": 5}
    )

    logger.info("Player game logs result:")
    logger.info(result.content[0].text)

    assert result.is_error is False
    assert len(result.content) > 0

    # Verify data contains expected information
    data_text = result.content[0].text
    assert "pts" in data_text.lower() or "PTS" in data_text


async def test_get_player_game_logs_advanced_stats(mcp_client: Client[FastMCPTransport]):
    """Test get_player_game_logs with advanced stats."""
    result = await mcp_client.call_tool(
        name="get_player_game_logs",
        arguments={
            "player_name": "LeBron James",
            "last_n_games": 3,
            "stat_type": "Advanced",
        }
    )

    logger.info("Advanced player game logs result:")
    logger.info(result.content[0].text)

    assert result.is_error is False
    assert len(result.content) > 0


async def test_get_player_game_logs_per_100_possessions(mcp_client: Client[FastMCPTransport]):
    """Test get_player_game_logs with per 100 possessions mode."""
    result = await mcp_client.call_tool(
        name="get_player_game_logs",
        arguments={
            "player_name": "Stephen Curry",
            "last_n_games": 5,
            "per_mode": "Per100Possessions",
        }
    )

    logger.info("Per 100 possessions game logs result:")
    logger.info(result.content[0].text)

    assert result.is_error is False
    assert len(result.content) > 0


async def test_get_player_game_logs_specific_season(mcp_client: Client[FastMCPTransport]):
    """Test get_player_game_logs for a specific season."""
    result = await mcp_client.call_tool(
        name="get_player_game_logs",
        arguments={
            "player_name": "Giannis Antetokounmpo",
            "last_n_games": 5,
            "season": "2023-24",
        }
    )

    logger.info("Specific season game logs result:")
    logger.info(result.content[0].text)

    assert result.is_error is False
    assert len(result.content) > 0


async def test_get_player_game_logs_per36(mcp_client: Client[FastMCPTransport]):
    """Test get_player_game_logs with per 36 minutes mode."""
    result = await mcp_client.call_tool(
        name="get_player_game_logs",
        arguments={
            "player_name": "Anthony Edwards",
            "last_n_games": 5,
            "per_mode": "Per36",
        }
    )

    logger.info("Per 36 minutes game logs result:")
    logger.info(result.content[0].text)

    assert result.is_error is False
    assert len(result.content) > 0


async def test_get_player_game_logs_invalid_player(mcp_client: Client[FastMCPTransport]):
    """Test error handling for non-existent player."""
    result = await mcp_client.call_tool(
        name="get_player_game_logs",
        arguments={"player_name": "Invalid Player Name XYZ"},
        raise_on_error=False
    )

    logger.info("Invalid player error:")
    logger.info(result.content[0].text)

    assert result.is_error is True
    assert "not found" in result.content[0].text


async def test_get_player_game_logs_invalid_stat_type(mcp_client: Client[FastMCPTransport]):
    """Test error handling for invalid stat type."""
    result = await mcp_client.call_tool(
        name="get_player_game_logs",
        arguments={
            "player_name": "LeBron James",
            "stat_type": "InvalidType",
        },
        raise_on_error=False
    )

    logger.info("Invalid stat type error:")
    logger.info(result.content[0].text)

    assert result.is_error is True
    assert "Invalid measure_type" in result.content[0].text


async def test_get_player_game_logs_invalid_per_mode(mcp_client: Client[FastMCPTransport]):
    """Test error handling for invalid per mode."""
    result = await mcp_client.call_tool(
        name="get_player_game_logs",
        arguments={
            "player_name": "LeBron James",
            "per_mode": "InvalidMode",
        },
        raise_on_error=False
    )

    logger.info("Invalid per mode error:")
    logger.info(result.content[0].text)

    assert result.is_error is True
    assert "Invalid per_mode" in result.content[0].text


async def test_get_player_game_logs_invalid_last_n_games_zero(mcp_client: Client[FastMCPTransport]):
    """Test error handling for last_n_games=0."""
    result = await mcp_client.call_tool(
        name="get_player_game_logs",
        arguments={
            "player_name": "LeBron James",
            "last_n_games": 0,
        },
        raise_on_error=False
    )

    logger.info("Invalid last_n_games (0) error:")
    logger.info(result.content[0].text)

    assert result.is_error is True
    assert "last_n_games must be between 1 and 82" in result.content[0].text


async def test_get_player_game_logs_invalid_last_n_games_negative(mcp_client: Client[FastMCPTransport]):
    """Test error handling for negative last_n_games."""
    result = await mcp_client.call_tool(
        name="get_player_game_logs",
        arguments={
            "player_name": "LeBron James",
            "last_n_games": -5,
        },
        raise_on_error=False
    )

    logger.info("Invalid last_n_games (negative) error:")
    logger.info(result.content[0].text)

    assert result.is_error is True
    assert "last_n_games must be between 1 and 82" in result.content[0].text


async def test_get_player_game_logs_invalid_last_n_games_too_large(mcp_client: Client[FastMCPTransport]):
    """Test error handling for last_n_games > 82."""
    result = await mcp_client.call_tool(
        name="get_player_game_logs",
        arguments={
            "player_name": "LeBron James",
            "last_n_games": 100,
        },
        raise_on_error=False
    )

    logger.info("Invalid last_n_games (too large) error:")
    logger.info(result.content[0].text)

    assert result.is_error is True
    assert "last_n_games must be between 1 and 82" in result.content[0].text
