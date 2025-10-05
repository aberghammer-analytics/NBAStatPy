# NBAStatPy

[![PyPI version](https://badge.fury.io/py/nbastatpy.svg)](https://badge.fury.io/py/nbastatpy)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![CI](https://github.com/aberghammer-analytics/NBAStatPy/workflows/Run%20Pytest/badge.svg)](https://github.com/aberghammer-analytics/NBAStatPy/actions)

## Overview

This is an easy-to-use wrapper for the `nba_api` package. The goal is to be able to easily access and find data for a player, game, team, or season.

The data is accessed through a class based on how you're searching for it. A quickstart example is shown below. Currently there are 4 classes:

- `Game`
- `Player`
- `Season`
- `Team`

## Quickstart

To get started you can import the class that represents the data you're searching for.

```{python}
from nbastatpy.player import Player
```

Then you build a player using either an ID from stats.nba.com or the player's name. When you're building the player object you can add additional search data like season, data format, or playoffs vs. regular season.

```{python}
player = Player(
    "Giannis",
    season="2020",
    playoffs=True,
    permode="PerGame"
)
```

Once you have the player object, you can get different datasets based on the criteria. For instance, you can get the awards the player has won by doing the following:

```{python}
player.get_awards()
```

This returns a pandas dataframe with the awards won by the player each year.

There are a lot of endpoints and various arguments for more complex queries like tracking and synergy datasets.

## Data Standardization

NBAStatPy includes comprehensive built-in data standardization to ensure consistency across all datasets. This makes your data analysis-ready with clean, predictable formats.

### Features

The standardization system provides:

#### Core Transformations
- **ID Standardization**: All IDs (player_id, team_id, game_id, etc.) zero-padded to 10 digits
- **Column Name Normalization**: All columns converted to lowercase with consistent naming
- **Date Parsing**: Automatic conversion of date fields to date objects
- **Time Conversions**: Minutes:seconds format → total seconds (e.g., "12:30" → 750)
- **Type Enforcement**: Integers, floats, and strings properly typed based on column semantics

#### Advanced Transformations
- **Height Conversion**: Feet-inches format → total inches (e.g., "6-11" → 83)
- **Weight Normalization**: Standardized to numeric pounds
- **Position Standardization**: Consistent abbreviations (e.g., "Point Guard" → "PG")
- **Matchup Parsing**: Game matchups split into home_team and away_team
- **W/L Standardization**: Win/loss indicators normalized to "W" or "L"
- **Clock Time Parsing**: Play-by-play clock format → seconds (e.g., "PT11M23S" → 683)

#### Metadata Addition
- Season ID and playoff flags for season data
- Standardization timestamps (optional)
- Data source tracking (optional)

### Quick Start

Simply add `standardize=True` to any `get_*` method:

```python
from nbastatpy.player import Player
from nbastatpy.season import Season
from nbastatpy.game import Game

# Player data with standardization
player = Player("Giannis", season="2023", playoffs=False)
stats = player.get_common_info(standardize=True)
# ✓ player_id: "0000203507" (zero-padded)
# ✓ height_inches: 83 (converted from "6-11")
# ✓ weight: 242 (numeric pounds)
# ✓ birthdate: date object

# Season data with standardization
season = Season(season_year="2023", playoffs=False)
player_stats = season.get_player_stats(standardize=True)
# ✓ All column names lowercase
# ✓ season_id: "2023-24" added
# ✓ is_playoffs: "REGULAR_SEASON" added
# ✓ Integer stats: Int64 type (handles nulls)

# Game data with standardization
game = Game(game_id="0022301148")
boxscore = game.get_boxscore(standardize=True)
# ✓ game_id: "0022301148" (zero-padded)
# ✓ seconds: 750 (from "12:30" minutes)
# ✓ matchup parsed: home_team, away_team extracted
# ✓ wl: "W" or "L" (normalized)
```

### Supported Methods

**100% Coverage**: All `get_*` methods across all classes support `standardize=True`:

- **Season class**: 35+ methods (lineups, shots, tracking, synergy, defense, etc.)
- **Player class**: 17+ methods (common info, career stats, game logs, etc.)
- **Game class**: 13+ methods (boxscore, advanced, tracking, play-by-play, etc.)
- **Team class**: 21+ methods (roster, stats, splits, etc.)

### Standalone Standardization

You can also standardize any DataFrame directly using the standardization functions:

```python
from nbastatpy.standardize import standardize_dataframe

# Standardize player data
df = standardize_dataframe(df, data_type='player')

# Standardize game data
df = standardize_dataframe(df, data_type='game')

# Standardize season data with metadata
df = standardize_dataframe(
    df,
    data_type='season',
    season='2023-24',
    playoffs=True,
    add_metadata=True  # Adds standardization timestamp
)

# Standardize team data
df = standardize_dataframe(
    df,
    data_type='team',
    season='2023-24',
    playoffs=False
)
```

### Standardization Details

#### Column Type Mappings

The standardization engine recognizes 200+ NBA stat columns:

**Integer Columns** (98 fields):
- Game stats: `gp`, `gs`, `w`, `l`, `fgm`, `fga`, `fg3m`, `pts`, etc.
- Advanced stats: `touches`, `drives`, `passes`, `deflections`, etc.
- Shot locations: `restricted_area_fgm`, `paint_fga`, `corner_three_fgm`, etc.

**Float Columns** (82 fields):
- Percentages: `fg_pct`, `fg3_pct`, `ts_pct`, `efg_pct`, `usg_pct`, etc.
- Ratings: `off_rating`, `def_rating`, `net_rating`, `pie`, etc.
- Tracking: `dist_miles`, `avg_speed`, `time_of_poss`, etc.

**String Columns** (47 fields):
- Names: `player_name`, `team_name`, `team_abbreviation`, etc.
- Categories: `position`, `college`, `matchup`, `wl`, etc.

#### ID Field Handling

All ID fields automatically zero-padded and standardized:
```python
# Before: 203507
# After:  "0000203507"

# Handles multiple ID types:
# - player_id, team_id, game_id
# - off_player_id, def_player_id
# - player1_id through player5_id (lineups)
```

#### Date Handling

Supports multiple date formats with automatic parsing:
```python
# ISO with time: "2024-01-15T00:00:00" → date(2024, 1, 15)
# ISO date: "2024-01-15" → date(2024, 1, 15)
# US format: "01/15/2024" → date(2024, 1, 15)
```

#### Special Field Conversions

**Height**: `"6-11"` → `83` (as `height_inches`)
**Weight**: `"242 lbs"` → `242` (as integer)
**Minutes**: `"12:30"` → `750` (as `seconds`)
**Matchup**: `"TOR @ BOS"` → `away_team="TOR"`, `home_team="BOS"`
**Clock**: `"PT11M23S"` → `683` (as `clock_seconds`)

### Data Validation

Validate your standardized data to ensure quality:

```python
from nbastatpy.validators import validate_dataframe

result = validate_dataframe(
    df,
    required_columns={'player_id', 'team_id'},
    range_rules={'age': (15, 50), 'pts': (0, 100)}
)

if not result.passed:
    print(result)  # Shows detailed errors and warnings
```

### Performance Notes

- Standardization adds minimal overhead (~50-100ms for typical DataFrames)
- All transformations are fail-safe with logging (data never lost)
- Uses pandas nullable types (Int64, Float64) for proper null handling
- Backward compatible: defaults to `standardize=False`

### Examples

#### Clean Player Data for Analysis
```python
from nbastatpy.player import Player
import pandas as pd

player = Player("LeBron James")
info = player.get_common_info(standardize=True)

# Now analysis-ready:
# - player_id is string "0000002544"
# - height_inches is integer 81
# - birthdate is date object for age calculations
# - All column names lowercase for easy access
```

#### Multi-Season Comparison
```python
from nbastatpy.season import Season

seasons = ["2021", "2022", "2023"]
dfs = []

for year in seasons:
    season = Season(season_year=year)
    df = season.get_player_stats(standardize=True)
    dfs.append(df)

# Concatenate with confidence - all schemas match!
combined = pd.concat(dfs, ignore_index=True)
# ✓ Consistent types across all seasons
# ✓ season_id column for grouping
# ✓ is_playoffs flag for filtering
```

#### Game Analysis with Clean Data
```python
from nbastatpy.game import Game

game = Game("0022301148")
pbp = game.get_playbyplay(standardize=True)

# Ready for analysis:
# - clock_seconds for time-based analysis
# - home_team and away_team extracted
# - All IDs standardized for joins
# - Proper types for aggregations
```
