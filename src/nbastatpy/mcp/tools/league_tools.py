from typing import Any, cast

import nba_api.stats.endpoints as nba

from nbastatpy import League
from nbastatpy.mcp.server import mcp
from nbastatpy.utils import LeaderStats, Validators


@mcp.tool()
def get_league_leaders(
    stat_category: str,
    season: str | None = None,
    per_mode: str = "PerGame",
    season_type: str = "Regular Season",
    limit: int = 25,
) -> list[dict]:
    """Get NBA league leaders for a specific statistic.

    Args:
        stat_category: Statistic to rank by (e.g., "PTS", "points", "REB", "rebounds", "AST", "assists", "STL", "BLK", "FG_PCT", "FG3_PCT").
        season: Season year (e.g., "2024", "2024-25"). Use "all-time" for career leaders. Defaults to current season.
        per_mode: Stats mode - "PerGame", "Totals", or "Per48". Defaults to "PerGame".
        season_type: "Regular Season" or "Playoffs". Defaults to "Regular Season".
        limit: Maximum number of leaders to return (1-100). Defaults to 25.
    """
    # Validate parameters
    Validators.validate_season_type(season_type)
    Validators.validate_limit(limit, min_val=1, max_val=100)

    # Check for all-time request (uses different endpoint)
    if season and season.lower() == "all-time":
        return _get_alltime_leaders(stat_category, per_mode, season_type, limit)

    # Use League class for season-specific leaders
    playoffs = season_type == "Playoffs"
    league_obj = League(season_year=season, playoffs=playoffs, permode=per_mode)
    leaders = league_obj.get_league_leaders(
        stat_category, limit=limit, standardize=True
    )

    return cast(list[dict[Any, Any]], leaders.to_dict(orient="records"))


def _get_alltime_leaders(
    stat_category: str, per_mode: str, season_type: str, limit: int
) -> list[dict]:
    """Fetch all-time career leaders using AllTimeLeadersGrids endpoint."""
    # Normalize stat category
    stat_key = stat_category.replace("_", "").replace("-", "").replace(" ", "").upper()
    if stat_key not in LeaderStats.STAT_CATEGORIES:
        valid = sorted(set(LeaderStats.STAT_CATEGORIES.values()))
        raise ValueError(f"Invalid stat_category '{stat_category}'. Valid: {valid}")
    stat_abbrev = LeaderStats.STAT_CATEGORIES[stat_key]

    attr_name = LeaderStats.ALLTIME_ATTR_MAP.get(stat_abbrev)
    if not attr_name:
        raise ValueError(f"All-time leaders not available for: {stat_abbrev}")

    per_mode_simple = "Totals" if "TOTAL" in per_mode.upper() else "PerGame"

    alltime = nba.AllTimeLeadersGrids(
        per_mode_simple=per_mode_simple,
        season_type=season_type,
        topx=limit,
    )

    df = getattr(alltime, attr_name).get_data_frame()
    return cast(list[dict[Any, Any]], df.to_dict(orient="records"))


@mcp.tool()
def get_league_player_stats(
    season: str | None = None,
    per_mode: str = "PerGame",
    season_type: str = "Regular Season",
    limit: int = 50,
) -> list[dict]:
    """Get league-wide player statistics for a season.

    Returns statistics for all NBA players in a given season, sorted by points
    scored by default. Useful for comparing players across the league.

    Args:
        season: Season year (e.g., "2024", "2024-25"). Defaults to current season.
        per_mode: How statistics are calculated:
            - "PerGame": Per game averages (default)
            - "Per36": Per 36 minutes
            - "Per100Possessions": Per 100 possessions
            - "Totals": Raw totals
        season_type: "Regular Season" or "Playoffs". Defaults to "Regular Season".
        limit: Maximum number of players to return (1-500). Defaults to 50.

    Returns:
        List of player statistics, each containing:
        - player_id, player_name, team_abbreviation
        - gp: Games played
        - min: Minutes per game
        - pts, reb, ast, stl, blk, tov: Core stats
        - fg_pct, fg3_pct, ft_pct: Shooting percentages
        - plus_minus: Plus/minus rating

    Examples:
        - Get top 50 players: get_league_player_stats()
        - Get playoff stats: get_league_player_stats(season_type="Playoffs")
        - Get per-36 stats: get_league_player_stats(per_mode="Per36")
    """
    # Validate parameters
    Validators.validate_season_type(season_type)
    Validators.validate_limit(limit, min_val=1, max_val=500)

    playoffs = season_type == "Playoffs"
    league = League(season_year=season, playoffs=playoffs, permode=per_mode)

    df = league.get_player_stats(standardize=True)

    # Sort by points and limit results
    pts_col = "pts" if "pts" in df.columns else "PTS"
    if pts_col in df.columns:
        df = df.sort_values(by=pts_col, ascending=False)

    df = df.head(limit)

    return cast(list[dict[Any, Any]], df.to_dict(orient="records"))


@mcp.tool()
def get_league_team_stats(
    season: str | None = None,
    per_mode: str = "PerGame",
    season_type: str = "Regular Season",
) -> list[dict]:
    """Get league-wide team statistics for a season.

    Returns statistics for all 30 NBA teams in a given season.
    Useful for comparing team performance across the league.

    Args:
        season: Season year (e.g., "2024", "2024-25"). Defaults to current season.
        per_mode: How statistics are calculated:
            - "PerGame": Per game averages (default)
            - "Per100Possessions": Per 100 possessions
            - "Totals": Raw totals
        season_type: "Regular Season" or "Playoffs". Defaults to "Regular Season".

    Returns:
        List of team statistics, each containing:
        - team_id, team_name, team_abbreviation
        - gp: Games played
        - w, l, w_pct: Wins, losses, win percentage
        - min: Minutes per game
        - pts, reb, ast, stl, blk, tov: Core stats
        - fg_pct, fg3_pct, ft_pct: Shooting percentages
        - plus_minus: Plus/minus rating

    Examples:
        - Get all team stats: get_league_team_stats()
        - Get playoff team stats: get_league_team_stats(season_type="Playoffs")
        - Get 2023 season stats: get_league_team_stats(season="2023")
    """
    # Validate parameters
    Validators.validate_season_type(season_type)

    playoffs = season_type == "Playoffs"
    league = League(season_year=season, playoffs=playoffs, permode=per_mode)

    df = league.get_team_stats(standardize=True)

    return cast(list[dict[Any, Any]], df.to_dict(orient="records"))
