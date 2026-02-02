"""End-to-end tests that make real API calls against NBA stats endpoints.

These tests verify that the library works correctly against the live NBA API.
They are skipped by default in CI — run with: uv run pytest -m e2e

Rate limiting: 1 second between API calls to avoid overloading NBA servers.
"""

from time import sleep

import pandas as pd
import pytest

from nbastatpy import Game, League, Player, Team

pytestmark = pytest.mark.e2e

# Shared delay between API calls
API_DELAY = 1.0


def wait():
    """Sleep between API calls to respect rate limits."""
    sleep(API_DELAY)


# ============================================================================
# Player Tests
# ============================================================================


class TestPlayerE2E:
    """End-to-end tests for the Player class."""

    def test_player_init_by_name(self):
        """Test that a player can be created by name."""
        player = Player("LeBron James")
        assert player.name == "LeBron James"
        assert player.id == 2544
        assert player.league == "NBA"

    def test_player_init_by_id(self):
        """Test that a player can be created by ID."""
        wait()
        player = Player("203999")  # Nikola Jokic
        assert player.id == 203999

    def test_player_career_stats_by_year(self):
        """Test that career stats by year returns a valid DataFrame."""
        wait()
        player = Player("LeBron James")
        stats = player.get_career_stats_by_year()
        assert isinstance(stats, pd.DataFrame)
        assert len(stats) > 0

    def test_player_game_logs(self):
        """Test that game logs return data for a recent season."""
        wait()
        player = Player("LeBron James", season_year="2024")
        game_logs = player.get_game_logs(last_n_games=5)
        assert isinstance(game_logs, pd.DataFrame)
        assert len(game_logs) > 0

    def test_player_common_info(self):
        """Test that common player info returns valid data."""
        wait()
        player = Player("LeBron James")
        info = player.get_common_info()
        assert isinstance(info, pd.DataFrame)
        assert len(info) > 0


# ============================================================================
# Team Tests
# ============================================================================


class TestTeamE2E:
    """End-to-end tests for the Team class."""

    def test_team_init(self):
        """Test that a team can be created by abbreviation."""
        wait()
        team = Team("MIL")
        assert team.abbreviation == "MIL"
        assert team.league == "NBA"

    def test_team_roster(self):
        """Test that team roster returns valid data."""
        wait()
        team = Team("MIL", season_year="2024")
        roster = team.get_roster()
        assert isinstance(roster, list)
        assert len(roster) > 0
        assert isinstance(roster[0], pd.DataFrame)

    def test_team_game_log(self):
        """Test that team game log returns valid data."""
        wait()
        team = Team("MIL", season_year="2024")
        game_log = team.get_game_log(last_n_games=5)
        assert isinstance(game_log, pd.DataFrame)
        assert len(game_log) > 0


# ============================================================================
# League Tests
# ============================================================================


class TestLeagueE2E:
    """End-to-end tests for the League class."""

    def test_league_init(self):
        """Test that a league can be created with various season formats."""
        league = League(2024)
        assert league.season == "2024-25"
        assert league.season_year == 2024

    def test_league_leaders(self):
        """Test that league leaders returns valid data."""
        wait()
        league = League(2024)
        leaders = league.get_league_leaders(stat_category="PTS")
        assert isinstance(leaders, pd.DataFrame)
        assert len(leaders) > 0

    def test_league_synergy_player(self):
        """Test that synergy play type data works (bug #1 fix)."""
        wait()
        league = League(2024)
        synergy = league.get_synergy_player(play_type="Transition")
        assert isinstance(synergy, pd.DataFrame)
        assert len(synergy) > 0

    def test_league_synergy_team(self):
        """Test that team synergy play type data works (bug #1 fix)."""
        wait()
        league = League(2024)
        synergy = league.get_synergy_team(play_type="Transition")
        assert isinstance(synergy, pd.DataFrame)
        assert len(synergy) > 0

    def test_league_player_stats(self):
        """Test that league-wide player stats return data."""
        wait()
        league = League(2024)
        stats = league.get_player_stats()
        assert isinstance(stats, pd.DataFrame)
        assert len(stats) > 0


# ============================================================================
# Game Tests
# ============================================================================


class TestGameE2E:
    """End-to-end tests for the Game class."""

    def test_game_init(self):
        """Test that a game can be created with a game ID."""
        game = Game("0022400001")
        assert game.game_id == "0022400001"

    def test_game_boxscore(self):
        """Test that a boxscore returns valid data."""
        wait()
        game = Game("0022400001")
        boxscore = game.get_boxscore()
        assert isinstance(boxscore, list)
        assert len(boxscore) > 0
        assert isinstance(boxscore[0], pd.DataFrame)


# ============================================================================
# MCP Tool Tests
# ============================================================================


class TestMCPToolsE2E:
    """End-to-end tests for MCP tools with real API calls."""

    @pytest.fixture
    async def live_mcp_client(self):
        """MCP client without mocks for real API testing."""
        from fastmcp import Client
        from nbastatpy.mcp.server import mcp

        async with Client(transport=mcp) as client:
            yield client

    async def test_mcp_league_leaders(self, live_mcp_client):
        """Test get_league_leaders MCP tool with real data."""
        wait()
        result = await live_mcp_client.call_tool(
            name="get_league_leaders",
            arguments={"stat_category": "PTS", "limit": 5},
        )
        assert not result.is_error
        assert len(result.content) > 0

    async def test_mcp_player_career_stats(self, live_mcp_client):
        """Test get_player_career_stats MCP tool with real data."""
        wait()
        result = await live_mcp_client.call_tool(
            name="get_player_career_stats",
            arguments={"player_name": "LeBron James"},
        )
        assert not result.is_error
        assert len(result.content) > 0

    async def test_mcp_player_play_type_stats(self, live_mcp_client):
        """Test get_player_play_type_stats MCP tool (bug #1 fix verification)."""
        wait()
        result = await live_mcp_client.call_tool(
            name="get_player_play_type_stats",
            arguments={
                "player_name": "LeBron James",
                "play_type": "Transition",
                "season": "2024",
            },
        )
        assert not result.is_error
        assert len(result.content) > 0

    async def test_mcp_team_play_type_stats(self, live_mcp_client):
        """Test get_team_play_type_stats MCP tool (bug #1 fix verification)."""
        wait()
        result = await live_mcp_client.call_tool(
            name="get_team_play_type_stats",
            arguments={
                "team_name": "MIL",
                "play_type": "Transition",
                "season": "2024",
            },
        )
        assert not result.is_error
        assert len(result.content) > 0

    async def test_mcp_team_roster(self, live_mcp_client):
        """Test get_team_roster MCP tool with real data."""
        wait()
        result = await live_mcp_client.call_tool(
            name="get_team_roster",
            arguments={"team_abbreviation": "MIL", "season": "2024"},
        )
        assert not result.is_error
        assert len(result.content) > 0
