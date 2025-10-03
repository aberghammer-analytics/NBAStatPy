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

NBAStatPy includes built-in data standardization to ensure consistency across all datasets. This feature:

- **Standardizes IDs**: Ensures player_id, team_id, and game_id are zero-padded to 10 digits
- **Normalizes column names**: Converts all column names to lowercase with consistent naming
- **Parses dates**: Properly converts date fields to date objects
- **Converts time formats**: Transforms minutes:seconds format to total seconds
- **Adds metadata**: Optionally includes season_id, is_playoffs flag, and timestamps
- **Validates data**: Checks data types, ranges, and completeness

### Using Standardization

Simply add `standardize=True` to any `get_*` method:

```python
from nbastatpy.player import Player

player = Player("Giannis", season="2023", playoffs=False)

# Get standardized player stats
stats = player.get_common_info(standardize=True)

# Player IDs are now zero-padded to 10 digits
# Column names are lowercase
# Height is converted to total inches
# Dates are properly parsed
```

### Standalone Standardization

You can also standardize any DataFrame directly:

```python
from nbastatpy.standardize import standardize_dataframe

# Standardize player data
df = standardize_dataframe(df, data_type='player')

# Standardize season data with context
df = standardize_dataframe(
    df,
    data_type='season',
    season='2023-24',
    playoffs=True
)
```

### Data Validation

Validate your standardized data:

```python
from nbastatpy.validators import validate_dataframe

result = validate_dataframe(
    df,
    required_columns={'player_id', 'team_id'},
    range_rules={'age': (15, 50), 'pts': (0, 100)}
)

if not result.passed:
    print(result)  # Shows errors and warnings
```
