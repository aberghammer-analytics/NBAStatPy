from nbastatpy import Player
from nbastatpy.mcp.server import mcp
from nbastatpy.utils import Formatter, PlayTypes


@mcp.tool()
def get_player_salary(player_name: str, season: str | None = None) -> list[dict]:
    """Get player salary history and projections.

    Args:
        player_name: Player name (e.g., "LeBron James", "Giannis")
        season: Filter to specific season (e.g., "2024", "2023-24", "20232024"). Returns all seasons if not provided.
    """
    season = Formatter.normalize_season(season) if season else None

    player = Player(player_name)
    salary = player.get_salary(standardize=True)

    if season:
        salary = salary[salary["season"] == season]
    return salary.to_dict(orient="records")


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
    season_year = Formatter.normalize_season_year(season) if season else None

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

    return game_logs.to_dict(orient="records")
