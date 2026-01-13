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
