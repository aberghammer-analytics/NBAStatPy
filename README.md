# NBAStatPy

[![PyPI version](https://badge.fury.io/py/nbastatpy.svg)](https://badge.fury.io/py/nbastatpy)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![CI](https://github.com/aberghammer-analytics/NBAStatPy/workflows/Run%20Pytest/badge.svg)](https://github.com/aberghammer-analytics/NBAStatPy/actions)

## Overview

A simple, easy-to-use wrapper for the `nba_api` package to access NBA data for players, games, teams, and seasons.

## Quick Start

```python
from nbastatpy.player import Player

# Create a player object
player = Player("Giannis", season="2023", playoffs=True)

# Get data
awards = player.get_awards()
stats = player.get_career_stats()
```

## Main Classes

- **Player** - Access player stats, career data, and awards
- **Game** - Get boxscores, play-by-play, and game details
- **League** - Query league-wide stats, lineups, and tracking data
- **Team** - Retrieve team rosters, stats, and splits


### Standalone Usage

```python
from nbastatpy.standardize import standardize_dataframe

df = standardize_dataframe(df, data_type='player')
```

## MCP Integration (AI Assistant Tools)

NBAStatPy includes a [Model Context Protocol (MCP)](https://modelcontextprotocol.io/) server that allows AI assistants like Claude to access NBA data directly.

### Available Tools

| Tool | Description |
|------|-------------|
| `get_player_salary` | Get player salary data by name |
| `get_player_game_logs` | Get recent game logs for a player |
| `get_player_career_stats` | Get season-by-season career statistics |
| `get_player_play_type_stats` | Get play type (synergy) stats for a player |
| `get_player_tracking_stats` | Get tracking stats (drives, touches, etc.) |
| `get_league_leaders` | Get league leaders for any stat category |
| `get_team_recent_games` | Get recent games for a team |
| `get_team_play_type_stats` | Get play type stats for a team |
| `get_team_tracking_stats` | Get tracking stats for a team |
| `get_recent_games_summary` | Get summary of recent NBA games |
| `get_recent_games_player_stats` | Get player stats from recent games |

### Claude Code Integration

Add to your Claude Code MCP settings (`~/.claude/settings.json`):

```json
{
  "mcpServers": {
    "nbastatpy": {
      "command": "uvx",
      "args": ["--from", "nbastatpy", "nbastatpy-mcp"]
    }
  }
}
```

Or with pip:

```json
{
  "mcpServers": {
    "nbastatpy": {
      "command": "python",
      "args": ["-m", "nbastatpy.mcp.server"]
    }
  }
}
```

### Running the MCP Server Manually

```bash
# With uvx (recommended)
uvx --from nbastatpy nbastatpy-mcp

# With uv
uv run python -m nbastatpy.mcp.server

# With pip install
python -m nbastatpy.mcp.server
```

## Installation

### Pip
```bash
pip install nbastatpy
```

### UV
```bash
uv add nbastatpy
```
