# nbastatpy/mcp/server.py
from fastmcp import FastMCP

mcp = FastMCP(name="nbastatpy")

# These imports register the tools via their @mcp.tool() decorators
from nbastatpy.mcp.tools import (  # noqa: E402, F401
    game_tools,
    league_tools,
    player_tools,
    team_tools,
)
