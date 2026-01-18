from typing import Any, cast

from nbastatpy import League, Team
from nbastatpy.mcp.server import mcp
from nbastatpy.utils import Formatter, PlayTypes


@mcp.tool()
def get_team_recent_games(
    team_abbreviation: str,
    last_n_games: int = 10,
    season: str | None = None,
    season_type: str = "Regular Season",
    include_opponent_stats: bool = True,
    include_advanced_stats: bool = False,
) -> list[dict]:
    """Get statistics from the last n games for a team.

    Returns game-by-game stats including points, rebounds, assists, shooting percentages,
    and optionally opponent stats and advanced metrics.

    Args:
        team_abbreviation: NBA team abbreviation (e.g., "MIL", "LAL", "BOS", "GSW").
        last_n_games: Number of recent games to retrieve (1-82). Defaults to 10.
        season: Season year (e.g., "2024", "2024-25"). Defaults to current season.
        season_type: "Regular Season" or "Playoffs". Defaults to "Regular Season".
        include_opponent_stats: Whether to include opponent stats for each game (OPP_PTS, OPP_REB, etc.). Defaults to True.
        include_advanced_stats: Whether to include advanced stats (OFF_RATING, DEF_RATING, NET_RATING, PACE, EFG_PCT, TS_PCT, PIE, FT_RATE, TOV_PCT, OREB_PCT). Slower due to additional API calls. Defaults to False.
    """
    # Normalize season format if provided
    season_year = str(Formatter.normalize_season_year(season)) if season else None

    playoffs = season_type == "Playoffs"
    team = Team(team_abbreviation, season_year=season_year, playoffs=playoffs)

    game_log = team.get_game_log(
        last_n_games=last_n_games,
        include_opponent_stats=include_opponent_stats,
        include_advanced_stats=include_advanced_stats,
        standardize=True,
    )

    return cast(list[dict[Any, Any]], game_log.to_dict(orient="records"))


@mcp.tool()
def get_team_play_type_stats(
    play_type: str = "all",
    team_name: str | None = None,
    offensive: bool = True,
    season: str | None = None,
    per_mode: str = "PerGame",
    season_type: str = "Regular Season",
) -> list[dict]:
    """Get NBA play type (synergy) statistics for teams.

    Returns play type data showing how teams perform in different situations like
    transition, isolation, pick-and-roll, spot-up shooting, post-ups, and more.
    Useful for understanding team offensive/defensive tendencies and efficiency.

    Args:
        play_type: Type of play to retrieve. Options:
            - "Transition": Fast break plays
            - "Isolation": One-on-one plays
            - "PRBallHandler": Pick-and-roll ball handler
            - "PRRollman": Pick-and-roll roll man
            - "Postup": Post-up plays
            - "Spotup": Spot-up (catch-and-shoot) plays
            - "Handoff": Handoff plays
            - "Cut": Cutting plays
            - "OffScreen": Off-screen plays
            - "OffRebound": Offensive rebound putbacks
            - "Misc": Miscellaneous plays
            - "all": All play types (default)
        team_name: Optional team name to filter results (e.g., "Lakers", "Bucks", "Warriors").
            Uses case-insensitive partial matching. If not provided, returns all teams.
        offensive: True for offensive stats, False for defensive. Defaults to True.
        season: Season year (e.g., "2024", "2024-25"). Defaults to current season.
        per_mode: "PerGame" or "Totals". Defaults to "PerGame".
        season_type: "Regular Season" or "Playoffs". Defaults to "Regular Season".

    Examples:
        - Get all isolation stats: get_team_play_type_stats(play_type="Isolation")
        - Get Lakers' play type stats: get_team_play_type_stats(team_name="Lakers")
        - Get all play types for Bucks: get_team_play_type_stats(play_type="all", team_name="Bucks")
        - Get defensive transition stats: get_team_play_type_stats(play_type="Transition", offensive=False)
    """
    # Normalize season year if provided
    season_year = str(Formatter.normalize_season_year(season)) if season else None

    # Determine if playoffs
    playoffs = season_type == "Playoffs"

    # Normalize and validate per_mode
    permode_key = per_mode.replace("_", "").replace("-", "").upper()
    if permode_key not in PlayTypes.PERMODE:
        valid_modes = sorted(set(PlayTypes.PERMODE.values()))
        raise ValueError(f"Invalid per_mode '{per_mode}'. Valid: {valid_modes}")
    normalized_permode = PlayTypes.PERMODE[permode_key]

    # Create League instance
    league = League(
        season_year=season_year, playoffs=playoffs, permode=normalized_permode
    )

    # Get synergy team data with standardization
    df = league.get_synergy_team(
        play_type=play_type, offensive=offensive, standardize=True
    )

    # Filter by team name if provided (case-insensitive partial match)
    if team_name:
        # Try to find the team name column (may be lowercase after standardization)
        name_col = None
        for col in df.columns:
            if col.lower() in ("team_name", "teamname"):
                name_col = col
                break

        if name_col:
            df = df[df[name_col].str.lower().str.contains(team_name.lower(), na=False)]

    return cast(list[dict[Any, Any]], df.to_dict(orient="records"))
