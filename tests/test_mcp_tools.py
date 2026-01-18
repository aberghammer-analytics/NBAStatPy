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
        name="get_player_salary", arguments={"player_name": "LeBron James"}
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
        name="get_league_leaders", arguments={"stat_category": "PTS", "limit": 10}
    )

    logger.info("League leaders (PTS) result:")
    logger.info(result.content[0].text)

    assert result.is_error is False
    assert len(result.content) > 0


async def test_get_league_leaders_alltime(mcp_client: Client[FastMCPTransport]):
    """Test all-time career leaders."""
    result = await mcp_client.call_tool(
        name="get_league_leaders",
        arguments={"stat_category": "points", "season": "all-time", "limit": 5},
    )

    logger.info("All-time leaders result:")
    logger.info(result.content[0].text)

    assert result.is_error is False
    assert len(result.content) > 0


async def test_get_league_leaders_specific_season(mcp_client: Client[FastMCPTransport]):
    """Test leaders for a specific season."""
    result = await mcp_client.call_tool(
        name="get_league_leaders",
        arguments={"stat_category": "rebounds", "season": "2023-24"},
    )

    logger.info("2023-24 rebounding leaders result:")
    logger.info(result.content[0].text)

    assert result.is_error is False
    assert len(result.content) > 0


async def test_get_team_recent_games_basic(mcp_client: Client[FastMCPTransport]):
    """Test get_team_recent_games tool with basic usage."""
    result = await mcp_client.call_tool(
        name="get_team_recent_games",
        arguments={"team_abbreviation": "MIL", "last_n_games": 5},
    )

    logger.info("Team recent games result:")
    logger.info(result.content[0].text)

    assert result.is_error is False
    assert len(result.content) > 0

    # Verify data contains expected information
    data_text = result.content[0].text
    assert "pts" in data_text.lower() or "PTS" in data_text


async def test_get_team_recent_games_with_opponent_stats(
    mcp_client: Client[FastMCPTransport],
):
    """Test get_team_recent_games with opponent stats included."""
    result = await mcp_client.call_tool(
        name="get_team_recent_games",
        arguments={
            "team_abbreviation": "LAL",
            "last_n_games": 3,
            "include_opponent_stats": True,
        },
    )

    logger.info("Team recent games with opponent stats:")
    logger.info(result.content[0].text)

    assert result.is_error is False
    assert len(result.content) > 0

    # Verify opponent stats are included
    data_text = result.content[0].text
    assert "opp_pts" in data_text.lower() or "OPP_PTS" in data_text


async def test_get_team_recent_games_specific_season(
    mcp_client: Client[FastMCPTransport],
):
    """Test get_team_recent_games with specific season."""
    result = await mcp_client.call_tool(
        name="get_team_recent_games",
        arguments={
            "team_abbreviation": "BOS",
            "last_n_games": 5,
            "season": "2023-24",
        },
    )

    logger.info("Team recent games for 2023-24 season:")
    logger.info(result.content[0].text)

    assert result.is_error is False
    assert len(result.content) > 0


async def test_get_player_game_logs_basic(mcp_client: Client[FastMCPTransport]):
    """Test get_player_game_logs tool with basic usage."""
    result = await mcp_client.call_tool(
        name="get_player_game_logs",
        arguments={"player_name": "LeBron James", "last_n_games": 5},
    )

    logger.info("Player game logs result:")
    logger.info(result.content[0].text)

    assert result.is_error is False
    assert len(result.content) > 0

    # Verify data contains expected information
    data_text = result.content[0].text
    assert "pts" in data_text.lower() or "PTS" in data_text


async def test_get_player_game_logs_advanced_stats(
    mcp_client: Client[FastMCPTransport],
):
    """Test get_player_game_logs with advanced stats."""
    result = await mcp_client.call_tool(
        name="get_player_game_logs",
        arguments={
            "player_name": "LeBron James",
            "last_n_games": 3,
            "stat_type": "Advanced",
        },
    )

    logger.info("Advanced player game logs result:")
    logger.info(result.content[0].text)

    assert result.is_error is False
    assert len(result.content) > 0


async def test_get_player_game_logs_per_100_possessions(
    mcp_client: Client[FastMCPTransport],
):
    """Test get_player_game_logs with per 100 possessions mode."""
    result = await mcp_client.call_tool(
        name="get_player_game_logs",
        arguments={
            "player_name": "Stephen Curry",
            "last_n_games": 5,
            "per_mode": "Per100Possessions",
        },
    )

    logger.info("Per 100 possessions game logs result:")
    logger.info(result.content[0].text)

    assert result.is_error is False
    assert len(result.content) > 0


async def test_get_player_game_logs_specific_season(
    mcp_client: Client[FastMCPTransport],
):
    """Test get_player_game_logs for a specific season."""
    result = await mcp_client.call_tool(
        name="get_player_game_logs",
        arguments={
            "player_name": "Giannis Antetokounmpo",
            "last_n_games": 5,
            "season": "2023-24",
        },
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
        },
    )

    logger.info("Per 36 minutes game logs result:")
    logger.info(result.content[0].text)

    assert result.is_error is False
    assert len(result.content) > 0


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


async def test_get_player_game_logs_invalid_stat_type(
    mcp_client: Client[FastMCPTransport],
):
    """Test error handling for invalid stat type."""
    result = await mcp_client.call_tool(
        name="get_player_game_logs",
        arguments={
            "player_name": "LeBron James",
            "stat_type": "InvalidType",
        },
        raise_on_error=False,
    )

    logger.info("Invalid stat type error:")
    logger.info(result.content[0].text)

    assert result.is_error is True
    assert "Invalid measure_type" in result.content[0].text


async def test_get_player_game_logs_invalid_per_mode(
    mcp_client: Client[FastMCPTransport],
):
    """Test error handling for invalid per mode."""
    result = await mcp_client.call_tool(
        name="get_player_game_logs",
        arguments={
            "player_name": "LeBron James",
            "per_mode": "InvalidMode",
        },
        raise_on_error=False,
    )

    logger.info("Invalid per mode error:")
    logger.info(result.content[0].text)

    assert result.is_error is True
    assert "Invalid per_mode" in result.content[0].text


async def test_get_player_game_logs_invalid_last_n_games_zero(
    mcp_client: Client[FastMCPTransport],
):
    """Test error handling for last_n_games=0."""
    result = await mcp_client.call_tool(
        name="get_player_game_logs",
        arguments={
            "player_name": "LeBron James",
            "last_n_games": 0,
        },
        raise_on_error=False,
    )

    logger.info("Invalid last_n_games (0) error:")
    logger.info(result.content[0].text)

    assert result.is_error is True
    assert "last_n_games must be between 1 and 82" in result.content[0].text


async def test_get_player_game_logs_invalid_last_n_games_negative(
    mcp_client: Client[FastMCPTransport],
):
    """Test error handling for negative last_n_games."""
    result = await mcp_client.call_tool(
        name="get_player_game_logs",
        arguments={
            "player_name": "LeBron James",
            "last_n_games": -5,
        },
        raise_on_error=False,
    )

    logger.info("Invalid last_n_games (negative) error:")
    logger.info(result.content[0].text)

    assert result.is_error is True
    assert "last_n_games must be between 1 and 82" in result.content[0].text


async def test_get_player_game_logs_invalid_last_n_games_too_large(
    mcp_client: Client[FastMCPTransport],
):
    """Test error handling for last_n_games > 82."""
    result = await mcp_client.call_tool(
        name="get_player_game_logs",
        arguments={
            "player_name": "LeBron James",
            "last_n_games": 100,
        },
        raise_on_error=False,
    )

    logger.info("Invalid last_n_games (too large) error:")
    logger.info(result.content[0].text)

    assert result.is_error is True
    assert "last_n_games must be between 1 and 82" in result.content[0].text


# ============================================================================
# Tests for get_recent_games_summary
# ============================================================================


async def test_get_recent_games_summary_basic(mcp_client: Client[FastMCPTransport]):
    """Test get_recent_games_summary with default parameters."""
    result = await mcp_client.call_tool(
        name="get_recent_games_summary", arguments={"last_n_days": 7}
    )

    logger.info("Recent games summary result:")
    logger.info(result.content[0].text)

    assert result.is_error is False
    assert len(result.content) > 0


async def test_get_recent_games_summary_historical_season(
    mcp_client: Client[FastMCPTransport],
):
    """Test get_recent_games_summary for a historical season.

    Note: For historical seasons, last_n_days filters from today's date,
    so results will be empty for completed seasons. This test verifies
    the tool handles this gracefully (returns empty list).
    """
    result = await mcp_client.call_tool(
        name="get_recent_games_summary",
        arguments={"last_n_days": 30, "season": "2023-24"},
    )

    logger.info("Historical season games summary:")
    # Historical season has no games in "last 30 days" - returns empty list
    assert result.is_error is False
    # The result content contains the serialized empty list "[]"
    if len(result.content) > 0:
        logger.info(result.content[0].text)


async def test_get_recent_games_summary_structure(mcp_client: Client[FastMCPTransport]):
    """Test that get_recent_games_summary returns properly structured data."""
    result = await mcp_client.call_tool(
        name="get_recent_games_summary", arguments={"last_n_days": 14}
    )

    assert result.is_error is False

    # Verify data contains expected structure keywords
    data_text = result.content[0].text
    # Should contain game structure elements
    assert "game_id" in data_text or "game_date" in data_text or "matchup" in data_text


async def test_get_recent_games_summary_invalid_days_zero(
    mcp_client: Client[FastMCPTransport],
):
    """Test error handling for last_n_days=0."""
    result = await mcp_client.call_tool(
        name="get_recent_games_summary",
        arguments={"last_n_days": 0},
        raise_on_error=False,
    )

    logger.info("Invalid last_n_days (0) error:")
    logger.info(result.content[0].text)

    assert result.is_error is True
    assert "last_n_days must be between 1 and 365" in result.content[0].text


async def test_get_recent_games_summary_invalid_days_negative(
    mcp_client: Client[FastMCPTransport],
):
    """Test error handling for negative last_n_days."""
    result = await mcp_client.call_tool(
        name="get_recent_games_summary",
        arguments={"last_n_days": -5},
        raise_on_error=False,
    )

    logger.info("Invalid last_n_days (negative) error:")
    logger.info(result.content[0].text)

    assert result.is_error is True
    assert "last_n_days must be between 1 and 365" in result.content[0].text


async def test_get_recent_games_summary_invalid_days_too_large(
    mcp_client: Client[FastMCPTransport],
):
    """Test error handling for last_n_days > 365."""
    result = await mcp_client.call_tool(
        name="get_recent_games_summary",
        arguments={"last_n_days": 500},
        raise_on_error=False,
    )

    logger.info("Invalid last_n_days (too large) error:")
    logger.info(result.content[0].text)

    assert result.is_error is True
    assert "last_n_days must be between 1 and 365" in result.content[0].text


# ============================================================================
# Tests for get_recent_games_player_stats
# ============================================================================


async def test_get_recent_games_player_stats_basic(
    mcp_client: Client[FastMCPTransport],
):
    """Test get_recent_games_player_stats with default parameters."""
    result = await mcp_client.call_tool(
        name="get_recent_games_player_stats", arguments={"last_n_days": 7}
    )

    logger.info("Recent games player stats result:")
    logger.info(result.content[0].text)

    assert result.is_error is False
    assert len(result.content) > 0


async def test_get_recent_games_player_stats_team_filter(
    mcp_client: Client[FastMCPTransport],
):
    """Test get_recent_games_player_stats filtered by team."""
    result = await mcp_client.call_tool(
        name="get_recent_games_player_stats",
        arguments={"last_n_days": 14, "team_abbreviation": "LAL"},
    )

    logger.info("Lakers player stats result:")
    logger.info(result.content[0].text)

    assert result.is_error is False
    assert len(result.content) > 0

    # Verify LAL appears in the output
    data_text = result.content[0].text
    assert "LAL" in data_text


async def test_get_recent_games_player_stats_historical_season(
    mcp_client: Client[FastMCPTransport],
):
    """Test get_recent_games_player_stats for a historical season.

    Note: For historical seasons, last_n_days filters from today's date,
    so results will be empty for completed seasons. This test verifies
    the tool handles this gracefully (returns empty list).
    """
    result = await mcp_client.call_tool(
        name="get_recent_games_player_stats",
        arguments={"last_n_days": 30, "season": "2023-24"},
    )

    logger.info("Historical season player stats:")
    # Historical season has no games in "last 30 days" - returns empty list
    assert result.is_error is False
    # The result content contains the serialized empty list "[]"
    if len(result.content) > 0:
        logger.info(result.content[0].text)


async def test_get_recent_games_player_stats_structure(
    mcp_client: Client[FastMCPTransport],
):
    """Test that get_recent_games_player_stats returns properly structured data."""
    result = await mcp_client.call_tool(
        name="get_recent_games_player_stats", arguments={"last_n_days": 14}
    )

    assert result.is_error is False

    # Verify data contains expected structure keywords
    data_text = result.content[0].text
    # Should contain player stats elements
    assert "player" in data_text.lower() or "pts" in data_text.lower()


async def test_get_recent_games_player_stats_invalid_days(
    mcp_client: Client[FastMCPTransport],
):
    """Test error handling for invalid last_n_days."""
    result = await mcp_client.call_tool(
        name="get_recent_games_player_stats",
        arguments={"last_n_days": 0},
        raise_on_error=False,
    )

    logger.info("Invalid last_n_days error:")
    logger.info(result.content[0].text)

    assert result.is_error is True
    assert "last_n_days must be between 1 and 365" in result.content[0].text


# ============================================================================
# Tests for get_player_career_stats
# ============================================================================


async def test_get_player_career_stats_basic(mcp_client: Client[FastMCPTransport]):
    """Test get_player_career_stats with default parameters."""
    result = await mcp_client.call_tool(
        name="get_player_career_stats", arguments={"player_name": "Stephen Curry"}
    )

    logger.info("Player career stats result:")
    logger.info(result.content[0].text)

    assert result.is_error is False
    assert len(result.content) > 0

    # Verify data contains expected information
    data_text = result.content[0].text
    assert "pts" in data_text.lower() or "PTS" in data_text


async def test_get_player_career_stats_advanced(mcp_client: Client[FastMCPTransport]):
    """Test get_player_career_stats with advanced stats.

    Note: This test may fail intermittently due to NBA API rate limiting or timeouts.
    """
    result = await mcp_client.call_tool(
        name="get_player_career_stats",
        arguments={
            "player_name": "LeBron James",
            "stat_type": "Advanced",
        },
        raise_on_error=False,
    )

    logger.info("Advanced career stats result:")
    if result.is_error:
        logger.warning(
            f"API error (likely timeout): {result.content[0].text if result.content else 'unknown'}"
        )
    elif result.content:
        logger.info(result.content[0].text)

    # Allow API timeouts - these are external service issues
    if result.is_error and result.content:
        error_text = result.content[0].text.lower()
        if "timeout" in error_text or "expecting value" in error_text:
            pytest.skip("NBA API timeout - skipping flaky test")

    assert result.is_error is False or "timeout" in str(result.content).lower()


async def test_get_player_career_stats_per36(mcp_client: Client[FastMCPTransport]):
    """Test get_player_career_stats with per 36 minutes mode.

    Note: This test may fail intermittently due to NBA API rate limiting or timeouts.
    """
    result = await mcp_client.call_tool(
        name="get_player_career_stats",
        arguments={
            "player_name": "Kevin Durant",
            "per_mode": "Per36",
        },
        raise_on_error=False,
    )

    logger.info("Per 36 career stats result:")
    if result.is_error:
        logger.warning(
            f"API error (likely timeout): {result.content[0].text if result.content else 'unknown'}"
        )
    elif result.content:
        logger.info(result.content[0].text)

    # Allow API timeouts - these are external service issues
    if result.is_error and result.content:
        error_text = result.content[0].text.lower()
        if "timeout" in error_text or "expecting value" in error_text:
            pytest.skip("NBA API timeout - skipping flaky test")

    assert result.is_error is False or "timeout" in str(result.content).lower()


async def test_get_player_career_stats_playoffs(mcp_client: Client[FastMCPTransport]):
    """Test get_player_career_stats for playoffs."""
    result = await mcp_client.call_tool(
        name="get_player_career_stats",
        arguments={
            "player_name": "LeBron James",
            "season_type": "Playoffs",
        },
    )

    logger.info("Playoffs career stats result:")
    logger.info(result.content[0].text)

    assert result.is_error is False
    assert len(result.content) > 0


async def test_get_player_career_stats_invalid_player(
    mcp_client: Client[FastMCPTransport],
):
    """Test error handling for non-existent player."""
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
# Tests for get_player_play_type_stats
# ============================================================================


async def test_get_player_play_type_stats_isolation(
    mcp_client: Client[FastMCPTransport],
):
    """Test get_player_play_type_stats for isolation plays."""
    result = await mcp_client.call_tool(
        name="get_player_play_type_stats", arguments={"play_type": "Isolation"}
    )

    logger.info("Player isolation stats result:")
    logger.info(result.content[0].text[:500])  # Truncate for readability

    assert result.is_error is False
    assert len(result.content) > 0


async def test_get_player_play_type_stats_with_player_filter(
    mcp_client: Client[FastMCPTransport],
):
    """Test get_player_play_type_stats filtered by player."""
    result = await mcp_client.call_tool(
        name="get_player_play_type_stats",
        arguments={
            "play_type": "Isolation",
            "player_name": "Kevin Durant",
        },
    )

    logger.info("Kevin Durant isolation stats result:")
    logger.info(result.content[0].text)

    assert result.is_error is False
    assert len(result.content) > 0

    # Verify Durant appears in the output
    data_text = result.content[0].text
    assert "durant" in data_text.lower() or "Kevin" in data_text


async def test_get_player_play_type_stats_all_types(
    mcp_client: Client[FastMCPTransport],
):
    """Test get_player_play_type_stats for all play types."""
    result = await mcp_client.call_tool(
        name="get_player_play_type_stats",
        arguments={
            "play_type": "all",
            "player_name": "Giannis",
        },
    )

    logger.info("Giannis all play types result:")
    logger.info(result.content[0].text[:500])  # Truncate for readability

    assert result.is_error is False
    assert len(result.content) > 0


async def test_get_player_play_type_stats_defensive(
    mcp_client: Client[FastMCPTransport],
):
    """Test get_player_play_type_stats for defensive stats.

    Note: Defensive player synergy data may return empty results from the NBA API
    for certain play types. An empty result is still a valid response.
    """
    result = await mcp_client.call_tool(
        name="get_player_play_type_stats",
        arguments={
            "play_type": "Transition",
            "offensive": False,
        },
    )

    logger.info("Defensive transition stats result:")
    if result.content:
        logger.info(result.content[0].text[:500])  # Truncate for readability
    else:
        logger.info("Empty result (no defensive data available)")

    # The tool should not error - empty results are valid for defensive stats
    assert result.is_error is False


# ============================================================================
# Tests for get_player_tracking_stats
# ============================================================================


async def test_get_player_tracking_stats_speed_distance(
    mcp_client: Client[FastMCPTransport],
):
    """Test get_player_tracking_stats for speed and distance."""
    result = await mcp_client.call_tool(
        name="get_player_tracking_stats", arguments={"track_type": "SpeedDistance"}
    )

    logger.info("Player speed/distance stats result:")
    logger.info(result.content[0].text[:500])  # Truncate for readability

    assert result.is_error is False
    assert len(result.content) > 0


async def test_get_player_tracking_stats_with_player_filter(
    mcp_client: Client[FastMCPTransport],
):
    """Test get_player_tracking_stats filtered by player."""
    result = await mcp_client.call_tool(
        name="get_player_tracking_stats",
        arguments={
            "track_type": "SpeedDistance",
            "player_name": "Ja Morant",
        },
    )

    logger.info("Ja Morant speed/distance stats result:")
    logger.info(result.content[0].text)

    assert result.is_error is False
    assert len(result.content) > 0


async def test_get_player_tracking_stats_drives(mcp_client: Client[FastMCPTransport]):
    """Test get_player_tracking_stats for drive statistics."""
    result = await mcp_client.call_tool(
        name="get_player_tracking_stats", arguments={"track_type": "Drives"}
    )

    logger.info("Player drive stats result:")
    logger.info(result.content[0].text[:500])  # Truncate for readability

    assert result.is_error is False
    assert len(result.content) > 0


async def test_get_player_tracking_stats_passing(mcp_client: Client[FastMCPTransport]):
    """Test get_player_tracking_stats for passing statistics.

    Note: Player filtering may return empty results if the player name doesn't
    match or if tracking data is not available for certain players.
    """
    result = await mcp_client.call_tool(
        name="get_player_tracking_stats",
        arguments={
            "track_type": "Passing",
            "player_name": "Nikola Jokic",
        },
    )

    logger.info("Jokic passing stats result:")
    if result.content:
        logger.info(result.content[0].text)
    else:
        logger.info("Empty result (player filtering may not have matched)")

    # The tool should not error - empty results are valid
    assert result.is_error is False


# ============================================================================
# Tests for get_team_play_type_stats
# ============================================================================


async def test_get_team_play_type_stats_transition(
    mcp_client: Client[FastMCPTransport],
):
    """Test get_team_play_type_stats for transition plays."""
    result = await mcp_client.call_tool(
        name="get_team_play_type_stats", arguments={"play_type": "Transition"}
    )

    logger.info("Team transition stats result:")
    logger.info(result.content[0].text[:500])  # Truncate for readability

    assert result.is_error is False
    assert len(result.content) > 0


async def test_get_team_play_type_stats_with_team_filter(
    mcp_client: Client[FastMCPTransport],
):
    """Test get_team_play_type_stats filtered by team."""
    result = await mcp_client.call_tool(
        name="get_team_play_type_stats",
        arguments={
            "play_type": "Transition",
            "team_name": "Warriors",
        },
    )

    logger.info("Warriors transition stats result:")
    logger.info(result.content[0].text)

    assert result.is_error is False
    assert len(result.content) > 0

    # Verify Warriors appears in the output
    data_text = result.content[0].text
    assert "warriors" in data_text.lower() or "Golden State" in data_text


async def test_get_team_play_type_stats_all_types(mcp_client: Client[FastMCPTransport]):
    """Test get_team_play_type_stats for all play types."""
    result = await mcp_client.call_tool(
        name="get_team_play_type_stats",
        arguments={
            "play_type": "all",
            "team_name": "Bucks",
        },
    )

    logger.info("Bucks all play types result:")
    logger.info(result.content[0].text[:500])  # Truncate for readability

    assert result.is_error is False
    assert len(result.content) > 0


async def test_get_team_play_type_stats_defensive(mcp_client: Client[FastMCPTransport]):
    """Test get_team_play_type_stats for defensive stats."""
    result = await mcp_client.call_tool(
        name="get_team_play_type_stats",
        arguments={
            "play_type": "Isolation",
            "offensive": False,
        },
    )

    logger.info("Defensive isolation stats result:")
    logger.info(result.content[0].text[:500])  # Truncate for readability

    assert result.is_error is False
    assert len(result.content) > 0


# ============================================================================
# Tests for get_team_tracking_stats
# ============================================================================


async def test_get_team_tracking_stats_passing(mcp_client: Client[FastMCPTransport]):
    """Test get_team_tracking_stats for passing statistics."""
    result = await mcp_client.call_tool(
        name="get_team_tracking_stats", arguments={"track_type": "Passing"}
    )

    logger.info("Team passing stats result:")
    logger.info(result.content[0].text[:500])  # Truncate for readability

    assert result.is_error is False
    assert len(result.content) > 0


async def test_get_team_tracking_stats_with_team_filter(
    mcp_client: Client[FastMCPTransport],
):
    """Test get_team_tracking_stats filtered by team."""
    result = await mcp_client.call_tool(
        name="get_team_tracking_stats",
        arguments={
            "track_type": "Passing",
            "team_name": "Celtics",
        },
    )

    logger.info("Celtics passing stats result:")
    logger.info(result.content[0].text)

    assert result.is_error is False
    assert len(result.content) > 0

    # Verify Celtics appears in the output
    data_text = result.content[0].text
    assert "celtics" in data_text.lower() or "Boston" in data_text


async def test_get_team_tracking_stats_drives(mcp_client: Client[FastMCPTransport]):
    """Test get_team_tracking_stats for drive statistics."""
    result = await mcp_client.call_tool(
        name="get_team_tracking_stats", arguments={"track_type": "Drives"}
    )

    logger.info("Team drive stats result:")
    logger.info(result.content[0].text[:500])  # Truncate for readability

    assert result.is_error is False
    assert len(result.content) > 0


async def test_get_team_tracking_stats_speed_distance(
    mcp_client: Client[FastMCPTransport],
):
    """Test get_team_tracking_stats for speed and distance."""
    result = await mcp_client.call_tool(
        name="get_team_tracking_stats",
        arguments={
            "track_type": "SpeedDistance",
            "team_name": "Lakers",
        },
    )

    logger.info("Lakers speed/distance stats result:")
    logger.info(result.content[0].text)

    assert result.is_error is False
    assert len(result.content) > 0
