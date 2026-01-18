from datetime import datetime, timedelta
from typing import Any

import pandas as pd

from nbastatpy import League
from nbastatpy.mcp.server import mcp
from nbastatpy.utils import Formatter, GameStatsColumns


def _parse_matchup(matchup: str) -> tuple[str, str, bool]:
    """Parse matchup string to extract teams and determine home/away.

    Args:
        matchup: Matchup string like "LAL vs. BOS" or "LAL @ BOS"

    Returns:
        Tuple of (team_abbrev, opponent_abbrev, is_home)
    """
    if " vs. " in matchup:
        parts = matchup.split(" vs. ")
        return parts[0], parts[1], True  # vs. means home
    elif " @ " in matchup:
        parts = matchup.split(" @ ")
        return parts[0], parts[1], False  # @ means away
    return matchup, "", True  # fallback


def _filter_by_date_range(df: pd.DataFrame, last_n_days: int) -> pd.DataFrame:
    """Filter DataFrame to only include rows within the last n days.

    Args:
        df: DataFrame with game_date column
        last_n_days: Number of days to look back

    Returns:
        Filtered DataFrame
    """
    df = df.copy()
    df["game_date_parsed"] = pd.to_datetime(df["game_date"], errors="coerce")
    cutoff_date = datetime.now() - timedelta(days=last_n_days)
    return df[df["game_date_parsed"] >= cutoff_date]


@mcp.tool()
def get_recent_games_summary(
    last_n_days: int = 7,
    season: str | None = None,
    season_type: str = "Regular Season",
) -> list[dict]:
    """Get NBA game summaries for the last N days.

    Returns game scores, matchups, and team statistics for all games
    played within the specified time period. Each game includes both
    teams' stats for easy comparison.

    Use this tool to answer questions like "What games were played this weekend?"
    or "Give me a summary of yesterday's NBA games."

    Args:
        last_n_days: Number of days to look back (1-365). Defaults to 7.
            - Use 1 for yesterday's games
            - Use 2-3 for weekend games
            - Use 7 for past week
        season: Season year (e.g., "2024", "2024-25"). Defaults to current season.
        season_type: "Regular Season" or "Playoffs". Defaults to "Regular Season".

    Returns:
        List of game summaries, each containing:
        - game_id, game_date, matchup (e.g., "LAL vs. BOS")
        - home_team: abbreviation, score, result (W/L), and stats
        - away_team: abbreviation, score, result (W/L), and stats

    Examples:
        - Get last week's games: get_recent_games_summary(last_n_days=7)
        - Get weekend games: get_recent_games_summary(last_n_days=3)
        - Get playoff games: get_recent_games_summary(season_type="Playoffs")
    """
    # Validation
    if last_n_days < 1 or last_n_days > 365:
        raise ValueError(f"last_n_days must be between 1 and 365, got {last_n_days}")

    # Setup League instance
    season_year = Formatter.normalize_season_year(season) if season else None
    playoffs = season_type == "Playoffs"
    league = League(season_year=season_year, playoffs=playoffs)

    # Get all team games (1 API call)
    team_games = league.get_team_games(standardize=True)

    # Filter to recent games
    recent_games = _filter_by_date_range(team_games, last_n_days)

    if len(recent_games) == 0:
        return []

    # Group by game_id and build structured output
    results = []
    for game_id in recent_games["game_id"].unique():
        game_rows = recent_games[recent_games["game_id"] == game_id]

        # Get game date (same for both rows)
        game_date = game_rows["game_date"].iloc[0]
        if hasattr(game_date, "strftime"):
            game_date = game_date.strftime("%Y-%m-%d")
        else:
            game_date = str(game_date)

        # Process each team's data
        home_team_data = None
        away_team_data = None

        for _, row in game_rows.iterrows():
            team_abbrev, opponent_abbrev, is_home = _parse_matchup(row["matchup"])

            # Build stats dict
            stats = {}
            for col in GameStatsColumns.TEAM_STATS:
                if col in row.index:
                    val = row[col]
                    # Convert numpy types to Python types
                    if pd.notna(val):
                        if isinstance(val, (int, float)):
                            stats[col] = float(val) if "pct" in col else int(val)
                        else:
                            stats[col] = val

            team_data = {
                "abbreviation": team_abbrev,
                "score": int(row["pts"]) if pd.notna(row.get("pts")) else 0,
                "result": row.get("wl", ""),
                "stats": stats,
            }

            if is_home:
                home_team_data = team_data
            else:
                away_team_data = team_data

        # Build matchup string
        if home_team_data and away_team_data:
            matchup_str = (
                f"{home_team_data['abbreviation']} vs. {away_team_data['abbreviation']}"
            )
        else:
            matchup_str = game_rows["matchup"].iloc[0]

        game_summary = {
            "game_id": game_id,
            "game_date": game_date,
            "matchup": matchup_str,
            "home_team": home_team_data,
            "away_team": away_team_data,
        }
        results.append(game_summary)

    # Sort by date (most recent first)
    results.sort(key=lambda x: x["game_date"], reverse=True)

    return results


@mcp.tool()
def get_recent_games_player_stats(
    last_n_days: int = 7,
    season: str | None = None,
    season_type: str = "Regular Season",
    team_abbreviation: str | None = None,
) -> list[dict]:
    """Get full player boxscores for NBA games in the last N days.

    Returns detailed player statistics for all games played within
    the specified time period. Can optionally filter to a specific team.

    Use this tool to answer questions like "How did LeBron perform this week?"
    or "Show me all player stats from games played over the weekend."

    Args:
        last_n_days: Number of days to look back (1-365). Defaults to 7.
            - Use 1 for yesterday's games
            - Use 2-3 for weekend games
            - Use 7 for past week
        season: Season year (e.g., "2024", "2024-25"). Defaults to current season.
        season_type: "Regular Season" or "Playoffs". Defaults to "Regular Season".
        team_abbreviation: Optional NBA team abbreviation to filter results
            (e.g., "LAL", "BOS", "MIL"). If provided, only returns players from
            games involving that team.

    Returns:
        List of games, each containing:
        - game_id, game_date, matchup
        - players: list of player stats (name, team, points, rebounds, assists, etc.)

    Examples:
        - All player stats for last week: get_recent_games_player_stats(last_n_days=7)
        - Lakers player stats: get_recent_games_player_stats(team_abbreviation="LAL")
        - Weekend playoff stats: get_recent_games_player_stats(last_n_days=3, season_type="Playoffs")
    """
    # Validation
    if last_n_days < 1 or last_n_days > 365:
        raise ValueError(f"last_n_days must be between 1 and 365, got {last_n_days}")

    # Setup League instance
    season_year = Formatter.normalize_season_year(season) if season else None
    playoffs = season_type == "Playoffs"
    league = League(season_year=season_year, playoffs=playoffs)

    # Get all player games (1 API call)
    player_games = league.get_player_games(standardize=True)

    # Filter to recent games
    recent_games = _filter_by_date_range(player_games, last_n_days)

    if len(recent_games) == 0:
        return []

    # Optionally filter by team
    if team_abbreviation:
        team_abbrev_upper = team_abbreviation.upper()
        recent_games = recent_games[
            recent_games["team_abbreviation"].str.upper() == team_abbrev_upper
        ]
        if len(recent_games) == 0:
            return []

    # Group by game_id and build structured output
    results = []
    for game_id in recent_games["game_id"].unique():
        game_rows = recent_games[recent_games["game_id"] == game_id]

        # Get game date
        game_date = game_rows["game_date"].iloc[0]
        if hasattr(game_date, "strftime"):
            game_date = game_date.strftime("%Y-%m-%d")
        else:
            game_date = str(game_date)

        # Get matchup from first row
        matchup = game_rows["matchup"].iloc[0] if "matchup" in game_rows.columns else ""

        # Build player stats list
        players = []
        for _, row in game_rows.iterrows():
            player_stats: dict[str, Any] = {}
            for col in GameStatsColumns.PLAYER_STATS:
                if col in row.index:
                    val = row[col]
                    if pd.notna(val):
                        # Convert numpy types to Python types
                        if isinstance(val, (int, float)):
                            if "pct" in col:
                                player_stats[col] = float(val)
                            elif col in ["player_id"]:
                                player_stats[col] = int(val)
                            else:
                                player_stats[col] = (
                                    int(val) if float(val).is_integer() else float(val)
                                )
                        else:
                            player_stats[col] = str(val)
            players.append(player_stats)

        # Sort players by points scored (descending)
        players.sort(key=lambda x: x.get("pts", 0), reverse=True)

        game_data = {
            "game_id": game_id,
            "game_date": game_date,
            "matchup": matchup,
            "players": players,
        }
        results.append(game_data)

    # Sort by date (most recent first)
    results.sort(key=lambda x: x["game_date"], reverse=True)

    return results
