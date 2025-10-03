# Data Standardization Guide

This guide explains the data standardization features added to NBAStatPy.

## Overview

The standardization system ensures all NBA data returned by this package has consistent formatting, proper data types, and includes useful metadata. This is particularly important when combining data from multiple sources or building pipelines that require consistent data formats.

## Key Features

### 1. ID Standardization

All ID fields (player_id, team_id, game_id) are:
- Converted to strings
- Zero-padded to 10 digits
- Consistently named (e.g., `person_id` → `player_id`)

**Before:**
```python
PERSON_ID: 203507
TEAM_ID: 1610612749
```

**After:**
```python
player_id: "0000203507"
team_id: "1610612749"
```

### 2. Column Name Normalization

All column names are:
- Converted to lowercase
- Standardized across different endpoints

**Before:**
```python
PLAYER_NAME, TEAM_ABBREVIATION, FG_PCT
```

**After:**
```python
player_name, team_abbreviation, fg_pct
```

### 3. Date Parsing

Date fields are automatically parsed to proper date objects:
- `game_date`
- `birthdate`
- Other date fields

### 4. Time Conversions

Time fields in MM:SS format are converted to total seconds:
- `minutes` → `seconds`
- `matchupminutes` → `matchup_seconds`
- Play-by-play clock times

**Example:**
```python
min: "12:30" → seconds: 750
```

### 5. Special Conversions

#### Height Conversion
Player height in feet-inches format is converted to total inches:
```python
height: "6-11" → height_inches: 83
```

#### Playoff Flags
Standardized playoff indicators:
```python
is_playoffs: "PLAYOFFS" or "REGULAR_SEASON"
```

### 6. Metadata Enrichment

Optional metadata fields:
- `season_id`: Season identifier
- `is_playoffs`: Playoff flag
- `standardized_at`: Timestamp of standardization
- `source_endpoint`: Data source tracking

## Usage

### In-Method Standardization

The simplest way to use standardization is with the `standardize` parameter:

```python
from nbastatpy import Player, Game, Season, Team

# Player data
player = Player("Giannis", season_year="2023")
stats = player.get_common_info(standardize=True)

# Game data
game = Game("0022300123")
boxscore = game.get_boxscore(standardize=True)

# Season data
season = Season("2023", playoffs=False)
player_stats = season.get_player_stats(standardize=True)

# Team data
team = Team("MIL", season_year="2023")
roster = team.get_roster(standardize=True)
```

### Standalone Standardization

You can also standardize any DataFrame:

```python
from nbastatpy import standardize_dataframe

# Basic standardization
df_standardized = standardize_dataframe(df, data_type='player')

# With context for season/team data
df_standardized = standardize_dataframe(
    df,
    data_type='season',
    season='2023-24',
    playoffs=True,
    add_metadata=True
)
```

### Data Type Options

- `player`: Player-specific transformations (height, birthdate)
- `game`: Game-specific transformations (time conversions, clock)
- `season`: Season-specific transformations (season_id, playoff flag)
- `team`: Team-specific transformations (season metadata)
- `base`: Only basic transformations (IDs, columns, dates)

## Data Validation

Validate your standardized data:

```python
from nbastatpy import validate_dataframe

result = validate_dataframe(
    df,
    required_columns={'player_id', 'team_id'},
    range_rules={'age': (15, 50), 'pts': (0, 100)},
    max_null_pct=50.0
)

if not result.passed:
    print("Validation errors:")
    for error in result.errors:
        print(f"  - {error}")

if result.warnings:
    print("Validation warnings:")
    for warning in result.warnings:
        print(f"  - {warning}")
```

### Built-in Range Rules

The package includes NBA-specific range rules:

```python
from nbastatpy.validators import NBA_RANGE_RULES

# Includes ranges for:
# - age: (15, 50)
# - pts, reb, ast, stl, blk
# - fg_pct, fg3_pct, ft_pct
# - minutes, height_inches, weight
```

## Configuration

The standardization behavior is controlled by configuration classes in `nbastatpy.config`:

### ColumnTypes

Defines expected data types for common columns:
- `INTEGER_COLUMNS`: Age, games, stats
- `FLOAT_COLUMNS`: Percentages, metrics
- `STRING_COLUMNS`: Names, positions

### IDFields

Registry of ID field names and mappings:
- `ID_FIELDS`: Fields requiring zero-padding
- `ID_FIELD_MAPPING`: Inconsistent name mappings

### DateFields

Date field registry and parsing formats:
- `DATE_FIELDS`: Fields to parse as dates
- `DATE_FORMATS`: Formats to try when parsing

### TimeFields

Time conversion field registry:
- `MINUTES_SECONDS_FIELDS`: MM:SS format fields
- `SECONDS_FIELDS`: Already-converted fields

## Examples

### Complete Workflow

```python
from nbastatpy import Player, validate_dataframe
from nbastatpy.validators import NBA_RANGE_RULES

# Get standardized data
player = Player("Giannis", season_year="2023")
stats = player.get_season_career_totals(standardize=True)

# Validate the data
result = validate_dataframe(
    stats[0],  # season totals
    required_columns={'player_id', 'season_id'},
    range_rules={
        'age': NBA_RANGE_RULES['age'],
        'pts': NBA_RANGE_RULES['pts'],
    }
)

print(f"Data validated: {result.passed}")
```

### Batch Processing

```python
from nbastatpy import Season, standardize_dataframe

season = Season("2023")

# Get multiple datasets
player_stats = season.get_player_stats(standardize=True)
team_stats = season.get_team_stats(standardize=True)

# Both have consistent column names and ID formats
# Can be easily joined or combined
```

## Best Practices

1. **Use standardization for data pipelines**: Always enable standardization when building ETL pipelines or data warehouses

2. **Validate after standardization**: Run validation checks to ensure data quality

3. **Store standardized data**: Save the standardized version to avoid repeated processing

4. **Document your workflow**: Note which data has been standardized in your analysis

5. **Check for updates**: The standardization rules may be updated as new patterns are discovered

## Backward Compatibility

Standardization is **opt-in** by default:
- All existing code continues to work without changes
- No breaking changes to existing functionality
- `standardize=False` is the default for all methods

## Performance

Standardization adds minimal overhead:
- Typical overhead: <100ms for most datasets
- Zero-padding and column renaming are very fast
- Date parsing may take longer for large datasets
- Can be disabled when raw data is needed

## Troubleshooting

### Issue: IDs not properly formatted

Check that ID fields are in the `IDFields.ID_FIELDS` set in `config.py`. You can add custom ID fields:

```python
from nbastatpy.config import IDFields
IDFields.ID_FIELDS.add('my_custom_id')
```

### Issue: Dates not parsing correctly

The standardizer tries multiple date formats. If your dates aren't parsing, you may need to add a format to `DateFields.DATE_FORMATS`.

### Issue: Unexpected data types

Check the column type mappings in `ColumnTypes`. You can override these in your own processing.

## Contributing

To extend standardization:

1. Add new fields to appropriate config classes
2. Add transformation methods to standardizer classes
3. Add tests to verify behavior
4. Update documentation

See the `.scratch/bronze` directory for reference implementations used in production data pipelines.
