from nbastatpy import Team
from nbastatpy.mcp.server import mcp
from nbastatpy.utils import Formatter


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
    season_year = Formatter.normalize_season_year(season) if season else None

    playoffs = season_type == "Playoffs"
    team = Team(team_abbreviation, season_year=season_year, playoffs=playoffs)

    game_log = team.get_game_log(
        last_n_games=last_n_games,
        include_opponent_stats=include_opponent_stats,
        include_advanced_stats=include_advanced_stats,
        standardize=True,
    )

    return game_log.to_dict(orient="records")
