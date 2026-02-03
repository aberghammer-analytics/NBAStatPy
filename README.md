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

### WNBA Support

NBAStatPy supports WNBA data out of the box. Player and Team classes automatically detect whether a player or team belongs to the NBA or WNBA:

```python
from nbastatpy.player import Player
from nbastatpy.team import Team

# WNBA players are auto-detected
player = Player("A'ja Wilson")
print(player.league)  # "WNBA"
stats = player.get_career_stats()

# WNBA teams are auto-detected by abbreviation
team = Team("LVA")  # Las Vegas Aces
print(team.league)  # "WNBA"
roster = team.get_roster()
```

For league-wide WNBA data, pass the `league` parameter:

```python
from nbastatpy.league import League

wnba_season = League(2024, league="WNBA")
leaders = wnba_season.get_league_leaders(stat_category="PTS")
```

### Standalone Usage

```python
from nbastatpy.standardize import standardize_dataframe

df = standardize_dataframe(df, data_type='player')
```

## MCP Server

NBAStatPy includes a [Model Context Protocol (MCP)](https://modelcontextprotocol.io/) server that allows AI assistants like Claude to access NBA statistics data.

### Quick Start (No Installation Required)

Using [uvx](https://docs.astral.sh/uv/), you can run the MCP server directly without installing:

```bash
uvx nbastatpy
```

### Adding to Claude Code

**Option 1: CLI Command (Recommended)**
```bash
claude mcp add nbastatpy -- uvx nbastatpy
```

**Option 2: Manual Configuration**

Add to your `~/.claude.json` (user-level) or `.mcp.json` (project-level):

```json
{
  "mcpServers": {
    "nbastatpy": {
      "type": "stdio",
      "command": "uvx",
      "args": ["nbastatpy"]
    }
  }
}
```

**Option 3: With pip install**
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

### Available Tools

The MCP server provides tools for accessing NBA data:

| Tool | Description |
|------|-------------|
| `get_player_game_logs` | Get recent game logs for a player |
| `get_player_career_stats` | Get season-by-season career statistics |
| `get_player_play_type_stats` | Get play type (synergy) stats for a player |
| `get_player_tracking_stats` | Get tracking stats (drives, touches, etc.) |
| `get_player_info` | Get player biographical and career info |
| `get_league_leaders` | Get league leaders for any stat category |
| `get_league_player_stats` | Get league-wide player statistics |
| `get_league_team_stats` | Get league-wide team statistics |
| `get_team_recent_games` | Get recent games for a team |
| `get_team_play_type_stats` | Get play type stats for a team |
| `get_team_tracking_stats` | Get tracking stats for a team |
| `get_team_roster` | Get current team roster |
| `get_recent_games_summary` | Get summary of recent NBA games |
| `get_recent_games_player_stats` | Get player stats from recent games |
| `get_live_games` | Get currently live game data |
| `get_game_boxscore` | Get box score for a specific game |
| `get_game_playbyplay` | Get play-by-play data for a game |

## Installation

### Pip
```bash
pip install nbastatpy
```

### UV
```bash
uv add nbastatpy
```
