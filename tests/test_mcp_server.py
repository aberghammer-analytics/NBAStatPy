"""Tests for NBAStatPy MCP server initialization, configuration, and lifecycle."""

import asyncio

import pytest
from fastmcp import FastMCP
from fastmcp.client import Client
from fastmcp.client.transports import FastMCPTransport
from loguru import logger

from nbastatpy.mcp.server import mcp


@pytest.fixture
async def mcp_client():
    """Fixture providing FastMCP client for in-memory testing."""
    async with Client(transport=mcp) as client:
        yield client


@pytest.fixture
async def multiple_clients():
    """Fixture providing multiple FastMCP clients for concurrent testing."""
    clients = []
    try:
        for _ in range(3):
            client = Client(transport=mcp)
            await client.__aenter__()
            clients.append(client)
        yield clients
    finally:
        for client in clients:
            await client.__aexit__(None, None, None)


# ============================================================================
# Category 1: Server Initialization Tests
# ============================================================================


async def test_server_initialization():
    """Test that the server is properly initialized with correct configuration."""
    assert isinstance(mcp, FastMCP)
    assert mcp.name == "nbastatpy"
    logger.info(f"Server initialized: {mcp.name}")


async def test_server_accessible_by_client(mcp_client: Client[FastMCPTransport]):
    """Test that a client can successfully connect to and access the server."""
    # If we can list tools, the client can access the server
    tools = await mcp_client.list_tools()
    assert tools is not None
    assert len(tools) > 0
    logger.info(f"Client successfully accessed server and found {len(tools)} tools")


async def test_multiple_client_connections(multiple_clients: list[Client[FastMCPTransport]]):
    """Test that multiple clients can connect to the server simultaneously."""
    assert len(multiple_clients) == 3

    # Each client should be able to list tools independently
    results = await asyncio.gather(
        *[client.list_tools() for client in multiple_clients]
    )

    # All clients should get the same tool list
    assert all(len(result) > 0 for result in results)
    assert all(len(result) == len(results[0]) for result in results)

    logger.info(f"All {len(multiple_clients)} clients successfully connected and accessed server")


# ============================================================================
# Category 2: Tool Registration Tests
# ============================================================================


async def test_all_tools_registered(mcp_client: Client[FastMCPTransport]):
    """Test that all expected tools are registered on the server."""
    tools = await mcp_client.list_tools()

    tool_names = [tool.name for tool in tools]
    expected_tools = [
        "get_player_salary",
        "get_player_game_logs",
        "get_league_leaders",
        "get_team_recent_games",
        "get_recent_games_summary",
        "get_recent_games_player_stats",
    ]

    # Verify we have exactly the expected tools
    assert len(tool_names) == len(expected_tools)
    for expected_tool in expected_tools:
        assert expected_tool in tool_names

    logger.info(f"All {len(expected_tools)} expected tools are registered: {tool_names}")


async def test_tool_registration_count_by_module(mcp_client: Client[FastMCPTransport]):
    """Test that the correct number of tools are registered from each module."""
    tools = await mcp_client.list_tools()
    tool_names = [tool.name for tool in tools]

    # player_tools should contribute 3 tools (includes get_recent_games_player_stats)
    player_tools = [name for name in tool_names if "player" in name]
    assert len(player_tools) == 3

    # league_tools should contribute 1 tool
    league_tools = [name for name in tool_names if "league" in name]
    assert len(league_tools) == 1

    # team_tools should contribute 1 tool
    team_tools = [name for name in tool_names if "team" in name]
    assert len(team_tools) == 1

    # game_tools should contribute 1 tool (get_recent_games_summary; player_stats excluded due to "player" filter)
    game_tools = [name for name in tool_names if "game" in name and "player" not in name and "team" not in name]
    assert len(game_tools) == 1

    logger.info(f"Tool count by module - player: {len(player_tools)}, league: {len(league_tools)}, team: {len(team_tools)}, game: {len(game_tools)}")


async def test_no_duplicate_tools(mcp_client: Client[FastMCPTransport]):
    """Test that there are no duplicate tool registrations."""
    tools = await mcp_client.list_tools()
    tool_names = [tool.name for tool in tools]

    # Check for duplicates
    unique_names = set(tool_names)
    assert len(tool_names) == len(unique_names), f"Duplicate tools found: {tool_names}"

    logger.info("No duplicate tool registrations found")


async def test_all_tools_have_names(mcp_client: Client[FastMCPTransport]):
    """Test that all registered tools have valid names."""
    tools = await mcp_client.list_tools()

    for tool in tools:
        assert hasattr(tool, "name")
        assert tool.name is not None
        assert len(tool.name) > 0
        assert isinstance(tool.name, str)

    logger.info("All tools have valid names")


# ============================================================================
# Category 3: Tool Metadata & Schema Tests
# ============================================================================


async def test_all_tools_have_descriptions(mcp_client: Client[FastMCPTransport]):
    """Test that all tools have non-empty descriptions."""
    tools = await mcp_client.list_tools()

    for tool in tools:
        assert hasattr(tool, "description")
        assert tool.description is not None
        assert len(tool.description) > 0
        logger.info(f"Tool '{tool.name}' has description: {tool.description[:50]}...")


async def test_all_tools_have_input_schemas(mcp_client: Client[FastMCPTransport]):
    """Test that all tools have valid input schemas."""
    tools = await mcp_client.list_tools()

    for tool in tools:
        assert hasattr(tool, "inputSchema")
        assert tool.inputSchema is not None
        assert "properties" in tool.inputSchema or "type" in tool.inputSchema

    logger.info("All tools have valid input schemas")


async def test_get_player_salary_schema(mcp_client: Client[FastMCPTransport]):
    """Test the schema for get_player_salary tool."""
    tools = await mcp_client.list_tools()
    salary_tool = next(tool for tool in tools if tool.name == "get_player_salary")

    schema = salary_tool.inputSchema
    properties = schema.get("properties", {})

    # player_name should be required
    assert "player_name" in properties
    assert properties["player_name"]["type"] == "string"

    # season should be optional
    assert "season" in properties
    # Check if it allows null or is in required list
    required = schema.get("required", [])
    assert "player_name" in required
    assert "season" not in required or properties["season"].get("type") in ["string", ["string", "null"]]

    logger.info("get_player_salary schema validated")


async def test_get_player_game_logs_schema(mcp_client: Client[FastMCPTransport]):
    """Test the schema for get_player_game_logs tool."""
    tools = await mcp_client.list_tools()
    game_logs_tool = next(tool for tool in tools if tool.name == "get_player_game_logs")

    schema = game_logs_tool.inputSchema
    properties = schema.get("properties", {})
    required = schema.get("required", [])

    # player_name should be required
    assert "player_name" in properties
    assert "player_name" in required

    # last_n_games should be optional integer
    assert "last_n_games" in properties
    assert properties["last_n_games"]["type"] == "integer"

    # stat_type should be optional string
    assert "stat_type" in properties
    assert properties["stat_type"]["type"] == "string"

    # per_mode should be optional string
    assert "per_mode" in properties
    assert properties["per_mode"]["type"] == "string"

    logger.info("get_player_game_logs schema validated")


async def test_get_league_leaders_schema(mcp_client: Client[FastMCPTransport]):
    """Test the schema for get_league_leaders tool."""
    tools = await mcp_client.list_tools()
    leaders_tool = next(tool for tool in tools if tool.name == "get_league_leaders")

    schema = leaders_tool.inputSchema
    properties = schema.get("properties", {})
    required = schema.get("required", [])

    # stat_category should be required
    assert "stat_category" in properties
    assert "stat_category" in required
    assert properties["stat_category"]["type"] == "string"

    # limit should be optional integer
    assert "limit" in properties
    assert properties["limit"]["type"] == "integer"

    logger.info("get_league_leaders schema validated")


async def test_get_team_recent_games_schema(mcp_client: Client[FastMCPTransport]):
    """Test the schema for get_team_recent_games tool."""
    tools = await mcp_client.list_tools()
    team_games_tool = next(tool for tool in tools if tool.name == "get_team_recent_games")

    schema = team_games_tool.inputSchema
    properties = schema.get("properties", {})
    required = schema.get("required", [])

    # team_abbreviation should be required
    assert "team_abbreviation" in properties
    assert "team_abbreviation" in required
    assert properties["team_abbreviation"]["type"] == "string"

    # last_n_games should be optional integer
    assert "last_n_games" in properties
    assert properties["last_n_games"]["type"] == "integer"

    # Boolean flags should be typed correctly
    assert "include_opponent_stats" in properties
    assert properties["include_opponent_stats"]["type"] == "boolean"

    assert "include_advanced_stats" in properties
    assert properties["include_advanced_stats"]["type"] == "boolean"

    logger.info("get_team_recent_games schema validated")


async def test_tool_schemas_have_required_fields(mcp_client: Client[FastMCPTransport]):
    """Test that all tool schemas properly specify required vs optional parameters."""
    tools = await mcp_client.list_tools()

    for tool in tools:
        schema = tool.inputSchema

        # Schema should have a properties section
        assert "properties" in schema

        # Schema may have a required section (some tools may have all optional params)
        # But if it has required, it should be a list
        if "required" in schema:
            assert isinstance(schema["required"], list)

        logger.info(f"Tool '{tool.name}' has valid required/optional parameter specification")


# ============================================================================
# Category 4: Server Lifecycle Tests
# ============================================================================


async def test_server_context_manager():
    """Test that the server can be used in an async context manager."""
    async with Client(transport=mcp) as client:
        tools = await client.list_tools()
        assert len(tools) > 0

    # After exiting context, we should be able to create a new one
    async with Client(transport=mcp) as client2:
        tools2 = await client2.list_tools()
        assert len(tools2) > 0

    logger.info("Server context manager lifecycle works correctly")


async def test_concurrent_tool_calls(mcp_client: Client[FastMCPTransport]):
    """Test that multiple tool calls can be made concurrently without issues."""
    # Make multiple tool calls concurrently
    calls = [
        mcp_client.call_tool(
            name="get_league_leaders",
            arguments={"stat_category": "PTS", "limit": 5}
        ),
        mcp_client.call_tool(
            name="get_player_salary",
            arguments={"player_name": "LeBron James"}
        ),
        mcp_client.call_tool(
            name="get_league_leaders",
            arguments={"stat_category": "REB", "limit": 5}
        ),
    ]

    results = await asyncio.gather(*calls)

    # All calls should succeed
    assert len(results) == 3
    assert all(not result.is_error for result in results)

    logger.info("Concurrent tool calls completed successfully")


async def test_sequential_tool_calls(mcp_client: Client[FastMCPTransport]):
    """Test that sequential tool calls work correctly."""
    # Make several tool calls in sequence
    result1 = await mcp_client.call_tool(
        name="get_league_leaders",
        arguments={"stat_category": "PTS", "limit": 5}
    )
    assert not result1.is_error

    result2 = await mcp_client.call_tool(
        name="get_player_salary",
        arguments={"player_name": "LeBron James"}
    )
    assert not result2.is_error

    result3 = await mcp_client.call_tool(
        name="get_team_recent_games",
        arguments={"team_abbreviation": "MIL", "last_n_games": 3}
    )
    assert not result3.is_error

    logger.info("Sequential tool calls completed successfully")


# ============================================================================
# Category 5: Error Handling Tests
# ============================================================================


async def test_invalid_tool_name(mcp_client: Client[FastMCPTransport]):
    """Test that calling a non-existent tool raises an appropriate error."""
    with pytest.raises(Exception):  # FastMCP will raise an exception for invalid tool
        await mcp_client.call_tool(
            name="non_existent_tool",
            arguments={}
        )

    logger.info("Invalid tool name raises appropriate error")


async def test_server_resilience_after_tool_error(mcp_client: Client[FastMCPTransport]):
    """Test that the server continues working after a tool raises an error."""
    # First, cause an error by calling a tool with invalid arguments
    error_result = await mcp_client.call_tool(
        name="get_player_game_logs",
        arguments={"player_name": "Invalid Player Name XYZ"},
        raise_on_error=False
    )
    assert error_result.is_error

    # Now make a successful call to verify the server still works
    success_result = await mcp_client.call_tool(
        name="get_league_leaders",
        arguments={"stat_category": "PTS", "limit": 5}
    )
    assert not success_result.is_error

    logger.info("Server remains operational after tool error")


async def test_error_messages_are_informative(mcp_client: Client[FastMCPTransport]):
    """Test that error messages provide useful information."""
    # Call a tool with an invalid player name
    result = await mcp_client.call_tool(
        name="get_player_game_logs",
        arguments={"player_name": "Invalid Player XYZ 12345"},
        raise_on_error=False
    )

    assert result.is_error
    error_text = result.content[0].text

    # Error message should be informative
    assert len(error_text) > 0
    assert "not found" in error_text.lower() or "invalid" in error_text.lower() or "error" in error_text.lower()

    logger.info(f"Error message is informative: {error_text[:100]}")


async def test_concurrent_access_with_errors(multiple_clients: list[Client[FastMCPTransport]]):
    """Test that one client's error doesn't affect other clients."""
    # First client makes a successful call
    success_call = multiple_clients[0].call_tool(
        name="get_league_leaders",
        arguments={"stat_category": "PTS", "limit": 5}
    )

    # Second client makes an error call
    error_call = multiple_clients[1].call_tool(
        name="get_player_game_logs",
        arguments={"player_name": "Invalid Player Name"},
        raise_on_error=False
    )

    # Third client makes another successful call
    success_call2 = multiple_clients[2].call_tool(
        name="get_team_recent_games",
        arguments={"team_abbreviation": "MIL", "last_n_games": 3}
    )

    # Execute all concurrently
    results = await asyncio.gather(success_call, error_call, success_call2)

    # First and third should succeed, second should error
    assert not results[0].is_error
    assert results[1].is_error
    assert not results[2].is_error

    logger.info("Concurrent clients handle errors independently")
