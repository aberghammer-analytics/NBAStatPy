# nbastatpy/mcp/server.py
from fastmcp import FastMCP

mcp = FastMCP("nbastatpy", description="NBA statistics and analytics")

# These imports register the tools via their @mcp.tool() decorators
from nbastatpy.mcp.tools import (  # noqa: E402, F401
    game_tools,
    player_tools,
    season_tools,
    team_tools,
)
