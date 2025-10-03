"""Example demonstrating data standardization in NBAStatPy."""

from nbastatpy import Player, Season, standardize_dataframe, validate_dataframe

# Example 1: Using standardization with Player class
print("=" * 60)
print("Example 1: Player Data Standardization")
print("=" * 60)

player = Player("Giannis", season_year="2023", playoffs=False)

# Get player info without standardization
print("\nWithout standardization:")
info_unstandardized = player.get_common_info(standardize=False)
print(f"Columns (first 5): {list(info_unstandardized.columns)[:5]}")
print(f"Player ID: {info_unstandardized['PERSON_ID'].iloc[0]}")

# Get player info WITH standardization
print("\nWith standardization:")
info_standardized = player.get_common_info(standardize=True)
print(f"Columns (first 5): {list(info_standardized.columns)[:5]}")
print(f"Player ID (zero-padded): {info_standardized['player_id'].iloc[0]}")
if "height_inches" in info_standardized.columns:
    print(f"Height in inches: {info_standardized['height_inches'].iloc[0]}")

# Example 2: Using standardization with Season class
print("\n" + "=" * 60)
print("Example 2: Season Data Standardization")
print("=" * 60)

season = Season(season_year="2023", playoffs=False)

# Get player stats with standardization
print("\nGetting player stats with standardization...")
player_stats = season.get_player_stats(standardize=True)
print(f"Shape: {player_stats.shape}")
print(f"Columns include: {', '.join(list(player_stats.columns)[:10])}")

# Check if standardization metadata was added
if "season_id" in player_stats.columns:
    print(f"Season ID added: {player_stats['season_id'].iloc[0]}")
if "is_playoffs" in player_stats.columns:
    print(f"Playoff flag added: {player_stats['is_playoffs'].iloc[0]}")

# Example 3: Standalone standardization function
print("\n" + "=" * 60)
print("Example 3: Standalone Standardization")
print("=" * 60)

# Create a sample DataFrame
import pandas as pd

sample_data = pd.DataFrame(
    {
        "PLAYER_ID": [203507, 2544],
        "TEAM_ID": [1610612749, 1610612738],
        "PTS": [25.5, 30.2],
        "HEIGHT": ["6-11", "7-0"],
    }
)

print("\nOriginal DataFrame:")
print(sample_data)

# Standardize it
standardized = standardize_dataframe(sample_data, data_type="player")

print("\nStandardized DataFrame:")
print(standardized)

# Example 4: Data validation
print("\n" + "=" * 60)
print("Example 4: Data Validation")
print("=" * 60)

# Validate the standardized data
result = validate_dataframe(
    standardized,
    required_columns={"player_id", "team_id"},
    range_rules={"pts": (0, 100)},
)

print(f"\nValidation passed: {result.passed}")
if result.errors:
    print(f"Errors: {result.errors}")
if result.warnings:
    print(f"Warnings: {result.warnings}")
else:
    print("No errors or warnings!")

print("\n" + "=" * 60)
print("Examples Complete!")
print("=" * 60)
