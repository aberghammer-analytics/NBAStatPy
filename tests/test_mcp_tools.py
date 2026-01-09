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
