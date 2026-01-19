from typing import Any, cast

from nbastatpy import League, Player
from nbastatpy.mcp.server import mcp
from nbastatpy.utils import Formatter, PlayTypes


@mcp.tool()
def get_player_salary(player_name: str, season: str | None = None) -> list[dict]:
    """Get player salary history and projections.

    Args:
        player_name: Player name (e.g., "LeBron James", "Giannis")
        season: Filter to specific season (e.g., "2024", "2023-24", "20232024"). Returns all seasons if not provided.
    """
    season = Formatter.format_season(season) if season else None

    player = Player(player_name)
    salary = player.get_salary(standardize=True)

    if season:
        salary = salary[salary["season"] == season]
    return cast(list[dict[Any, Any]], salary.to_dict(orient="records"))


@mcp.tool()
def get_player_game_logs(
    player_name: str,
    last_n_games: int = 10,
    stat_type: str = "Base",
    per_mode: str = "PerGame",
    season: str | None = None,
    season_type: str = "Regular Season",
) -> list[dict]:
    """Get recent game logs for an NBA player with detailed statistics.

    Returns game-by-game stats for the player's most recent games. Supports different
    stat types (basic, advanced, usage, etc.) and different calculation modes
    (per game, per 36 minutes, per 100 possessions, etc.).

    Args:
        player_name: Player name (e.g., "LeBron James", "Giannis Antetokounmpo").
        last_n_games: Number of recent games to retrieve (1-82). Defaults to 10.
        stat_type: Type of statistics to return:
            - "Base": Traditional stats (PTS, REB, AST, FG%, etc.)
            - "Advanced": Advanced metrics (OFF_RATING, DEF_RATING, NET_RATING, TS%, etc.)
            - "Misc": Miscellaneous statistics
            - "Scoring": Detailed scoring breakdown
            - "Usage": Usage rate statistics
            Defaults to "Base".
        per_mode: How statistics are calculated:
            - "PerGame": Per game averages
            - "Per36": Per 36 minutes
            - "Per100Possessions": Per 100 possessions (pace-adjusted)
            - "PerMinute": Per minute
            - "Totals": Raw totals
            Defaults to "PerGame".
        season: Season year (e.g., "2024", "2024-25"). Defaults to current season.
        season_type: "Regular Season" or "Playoffs". Defaults to "Regular Season".

    Examples:
        - Get LeBron's last 5 games: get_player_game_logs("LeBron James", last_n_games=5)
        - Get Jokic's last 10 games with advanced stats: get_player_game_logs("Nikola Jokic", stat_type="Advanced")
        - Get Curry's per-100 stats: get_player_game_logs("Stephen Curry", per_mode="Per100Possessions")
    """
    # Validate last_n_games parameter
    if last_n_games < 1 or last_n_games > 82:
        raise ValueError(f"last_n_games must be between 1 and 82, got {last_n_games}")

    # Normalize season year if provided
    season_year = str(Formatter.normalize_season_year(season)) if season else None

    # Determine if playoffs
    playoffs = season_type == "Playoffs"

    # Normalize and validate per_mode using PlayTypes mapping
    permode_key = per_mode.replace("_", "").replace("-", "").upper()
    if permode_key not in PlayTypes.PERMODE:
        valid_modes = sorted(set(PlayTypes.PERMODE.values()))
        raise ValueError(f"Invalid per_mode '{per_mode}'. Valid: {valid_modes}")
    normalized_permode = PlayTypes.PERMODE[permode_key]

    # Create player instance
    player = Player(player_name, season_year=season_year, playoffs=playoffs)

    # Get game logs
    game_logs = player.get_game_logs(
        last_n_games=last_n_games,
        measure_type=stat_type,
        per_mode=normalized_permode,
        standardize=True,
    )

    return cast(list[dict[Any, Any]], game_logs.to_dict(orient="records"))


@mcp.tool()
def get_player_career_stats(
    player_name: str,
    stat_type: str = "Base",
    per_mode: str = "PerGame",
    season_type: str = "Regular Season",
) -> list[dict]:
    """Get a player's career statistics broken down by season.

    Returns season-by-season career stats for a player. Supports different stat types
    (traditional, advanced) and different calculation modes (per game, per 36, totals, etc.).

    Args:
        player_name: Player name (e.g., "LeBron James", "Giannis Antetokounmpo").
        stat_type: Type of statistics to return:
            - "Base": Traditional stats (PTS, REB, AST, FG%, etc.)
            - "Advanced": Advanced metrics (TS%, EFG%, OFF_RATING, DEF_RATING, etc.)
            - "Misc": Miscellaneous statistics
            - "Scoring": Detailed scoring breakdown
            - "Usage": Usage rate statistics
            Defaults to "Base".
        per_mode: How statistics are calculated:
            - "PerGame": Per game averages
            - "Per36": Per 36 minutes
            - "Per100Possessions": Per 100 possessions (pace-adjusted)
            - "Totals": Raw totals
            Defaults to "PerGame".
        season_type: "Regular Season" or "Playoffs". Defaults to "Regular Season".

    Examples:
        - Get LeBron's career stats: get_player_career_stats("LeBron James")
        - Get Jokic's advanced career stats: get_player_career_stats("Nikola Jokic", stat_type="Advanced")
        - Get Curry's career per-100 stats: get_player_career_stats("Stephen Curry", per_mode="Per100Possessions")
    """
    # Normalize and validate per_mode
    permode_key = per_mode.replace("_", "").replace("-", "").upper()
    if permode_key not in PlayTypes.PERMODE:
        valid_modes = sorted(set(PlayTypes.PERMODE.values()))
        raise ValueError(f"Invalid per_mode '{per_mode}'. Valid: {valid_modes}")
    normalized_permode = PlayTypes.PERMODE[permode_key]

    # Determine if playoffs
    playoffs = season_type == "Playoffs"

    # Create player instance
    player = Player(player_name, playoffs=playoffs)

    # Get career stats by year
    career_stats = player.get_career_stats_by_year(
        measure_type=stat_type,
        per_mode=normalized_permode,
        standardize=True,
    )

    return cast(list[dict[Any, Any]], career_stats.to_dict(orient="records"))


@mcp.tool()
def get_player_play_type_stats(
    play_type: str = "all",
    player_name: str | None = None,
    offensive: bool = True,
    season: str | None = None,
    per_mode: str = "PerGame",
    season_type: str = "Regular Season",
) -> list[dict]:
    """Get NBA play type (synergy) statistics for players.

    Returns play type data showing how players perform in different situations like
    isolation, pick-and-roll, spot-up shooting, post-ups, and more. Useful for
    understanding a player's offensive/defensive tendencies and efficiency.

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
        player_name: Optional player name to filter results (e.g., "LeBron", "Giannis").
            Uses case-insensitive partial matching. If not provided, returns all players.
        offensive: True for offensive stats, False for defensive. Defaults to True.
        season: Season year (e.g., "2024", "2024-25"). Defaults to current season.
        per_mode: "PerGame" or "Totals". Defaults to "PerGame".
        season_type: "Regular Season" or "Playoffs". Defaults to "Regular Season".

    Examples:
        - Get all isolation stats: get_player_play_type_stats(play_type="Isolation")
        - Get LeBron's play type stats: get_player_play_type_stats(player_name="LeBron")
        - Get all play types for Giannis: get_player_play_type_stats(play_type="all", player_name="Giannis")
        - Get defensive transition stats: get_player_play_type_stats(play_type="Transition", offensive=False)
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

    # Get synergy player data with standardization
    df = league.get_synergy_player(
        play_type=play_type, offensive=offensive, standardize=True
    )

    # Filter by player name if provided (case-insensitive partial match)
    if player_name:
        # Try to find the player name column (may be lowercase after standardization)
        name_col = None
        for col in df.columns:
            if col.lower() in ("player_name", "playername"):
                name_col = col
                break

        if name_col:
            df = df[
                df[name_col].str.lower().str.contains(player_name.lower(), na=False)
            ]

    return cast(list[dict[Any, Any]], df.to_dict(orient="records"))


@mcp.tool()
def get_player_tracking_stats(
    track_type: str = "Efficiency",
    player_name: str | None = None,
    season: str | None = None,
    per_mode: str = "PerGame",
    season_type: str = "Regular Season",
) -> list[dict]:
    """Get NBA tracking statistics for players.

    Returns player tracking data including speed/distance, possessions, drives, passing,
    catch-and-shoot, pull-up shots, post touches, paint touches, elbow touches, and more.
    Useful for understanding player movement, ball handling, and efficiency metrics.

    Args:
        track_type: Type of tracking data to retrieve. Options:
            - "SpeedDistance": Speed and distance traveled
            - "Possessions": Possession statistics
            - "CatchShoot": Catch and shoot stats
            - "PullUpShot": Pull-up shooting stats
            - "Defense": Defensive tracking
            - "Drives": Drive statistics
            - "Passing": Passing statistics
            - "ElbowTouch": Elbow touch stats
            - "PostTouch": Post touch stats
            - "PaintTouch": Paint touch stats
            - "Efficiency": Overall efficiency (default)
            - "all": All tracking types
        player_name: Optional player name to filter results (e.g., "LeBron", "Giannis").
            Uses case-insensitive partial matching. If not provided, returns all players.
        season: Season year (e.g., "2024", "2024-25"). Defaults to current season.
        per_mode: "PerGame" or "Totals". Defaults to "PerGame".
        season_type: "Regular Season" or "Playoffs". Defaults to "Regular Season".

    Examples:
        - Get all player drive stats: get_player_tracking_stats(track_type="Drives")
        - Get LeBron's tracking stats: get_player_tracking_stats(player_name="LeBron")
        - Get all speed/distance for Giannis: get_player_tracking_stats(track_type="SpeedDistance", player_name="Giannis")
        - Get all tracking types: get_player_tracking_stats(track_type="all")
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

    # Get tracking player data with standardization
    df = league.get_tracking_player(track_type=track_type, standardize=True)

    # Filter by player name if provided (case-insensitive partial match)
    if player_name:
        # Try to find the player name column (may be lowercase after standardization)
        name_col = None
        for col in df.columns:
            if col.lower() in ("player_name", "playername"):
                name_col = col
                break

        if name_col:
            df = df[
                df[name_col].str.lower().str.contains(player_name.lower(), na=False)
            ]

    return cast(list[dict[Any, Any]], df.to_dict(orient="records"))
