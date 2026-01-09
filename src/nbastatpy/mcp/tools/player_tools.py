from nbastatpy import Player
from nbastatpy.mcp.server import mcp
from nbastatpy.utils import Formatter


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
