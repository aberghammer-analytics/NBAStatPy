from datetime import datetime, timedelta
from typing import Any, cast

import pandas as pd

from nbastatpy import Game, League
from nbastatpy.mcp.server import mcp
from nbastatpy.utils import Formatter, GameStatsColumns, Validators


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
    league: str = "NBA",
) -> list[dict]:
    """Get NBA or WNBA game summaries for the last N days.

    Returns game scores, matchups, and team statistics for all games
    played within the specified time period. Each game includes both
    teams' stats for easy comparison.

    Use this tool to answer questions like "What games were played this weekend?"
    or "Give me a summary of yesterday's games."

    Args:
        last_n_days: Number of days to look back (1-365). Defaults to 7.
            - Use 1 for yesterday's games
            - Use 2-3 for weekend games
            - Use 7 for past week
        season: Season year (e.g., "2024", "2024-25"). Defaults to current season.
        season_type: "Regular Season" or "Playoffs". Defaults to "Regular Season".
        league: League to query - "NBA" or "WNBA". Defaults to "NBA".

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
    Validators.validate_last_n_days(last_n_days)
    Validators.validate_season_type(season_type)

    # Setup League instance
    season_year = Formatter.normalize_season_year(season) if season else None
    playoffs = season_type == "Playoffs"
    league_obj = League(season_year=season_year, playoffs=playoffs, league=league)

    # Get all team games (1 API call)
    team_games = league_obj.get_team_games(standardize=True)

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
    league: str = "NBA",
) -> list[dict]:
    """Get full player boxscores for NBA or WNBA games in the last N days.

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
        team_abbreviation: Optional team abbreviation to filter results
            (e.g., "LAL", "BOS", "LVA"). If provided, only returns players from
            games involving that team.
        league: League to query - "NBA" or "WNBA". Defaults to "NBA".

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
    Validators.validate_last_n_days(last_n_days)
    Validators.validate_season_type(season_type)

    # Setup League instance
    season_year = Formatter.normalize_season_year(season) if season else None
    playoffs = season_type == "Playoffs"
    league_obj = League(season_year=season_year, playoffs=playoffs, league=league)

    # Get all player games (1 API call)
    player_games = league_obj.get_player_games(standardize=True)

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


@mcp.tool()
def get_game_boxscore(
    game_id: str,
    include_advanced: bool = False,
    league: str = "NBA",
) -> dict:
    """Get the boxscore for a specific NBA or WNBA game.

    Returns detailed player and team statistics for a completed game.
    Optionally includes advanced metrics like offensive/defensive rating,
    true shooting percentage, and efficiency metrics.

    Args:
        game_id: The game ID (e.g., "0022301148", "22301148").
            IDs are automatically zero-padded to 10 digits.
        include_advanced: Whether to include advanced statistics.
            When True, returns additional metrics like OFF_RATING, DEF_RATING,
            NET_RATING, TS_PCT, EFG_PCT, PIE. Defaults to False.
        league: League for the game - "NBA" or "WNBA". Defaults to "NBA".

    Returns:
        Dictionary containing:
        - game_id: The formatted game ID
        - league: "NBA" or "WNBA"
        - player_stats: List of player boxscore entries
        - team_stats: List of team boxscore entries
        - advanced_player_stats: (if include_advanced=True) Advanced player metrics
        - advanced_team_stats: (if include_advanced=True) Advanced team metrics

    Examples:
        - Get NBA boxscore: get_game_boxscore("0022301148")
        - Get WNBA boxscore: get_game_boxscore("0041400406", league="WNBA")
        - With advanced stats: get_game_boxscore("0022301148", include_advanced=True)
    """
    game = Game(game_id, league=league)

    # Get traditional boxscore
    boxscore_dfs = game.get_boxscore(standardize=True)

    result: dict[str, Any] = {
        "game_id": game.game_id,
        "league": game.league,
        "player_stats": [],
        "team_stats": [],
    }

    # Player stats are in first DataFrame, team stats in last
    if boxscore_dfs and len(boxscore_dfs) > 0:
        result["player_stats"] = boxscore_dfs[0].to_dict(orient="records")
    if boxscore_dfs and len(boxscore_dfs) > 1:
        result["team_stats"] = boxscore_dfs[-1].to_dict(orient="records")

    # Include advanced stats if requested
    if include_advanced:
        advanced_dfs = game.get_advanced(standardize=True)
        if advanced_dfs and len(advanced_dfs) > 0:
            result["advanced_player_stats"] = advanced_dfs[0].to_dict(orient="records")
        if advanced_dfs and len(advanced_dfs) > 1:
            result["advanced_team_stats"] = advanced_dfs[-1].to_dict(orient="records")

    return cast(dict[str, Any], result)


@mcp.tool()
def get_game_playbyplay(
    game_id: str,
    period: int | None = None,
    league: str = "NBA",
) -> list[dict]:
    """Get play-by-play data for a specific NBA or WNBA game.

    Returns a chronological list of all plays in the game, including scores,
    shot attempts, turnovers, fouls, substitutions, and other events.

    Args:
        game_id: The game ID (e.g., "0022301148", "22301148").
            IDs are automatically zero-padded to 10 digits.
        period: Optional period to filter (1-4 for quarters, 5+ for OT).
            If not provided, returns all periods.
        league: League for the game - "NBA" or "WNBA". Defaults to "NBA".

    Returns:
        List of play-by-play entries, each containing:
        - game_id: Game identifier
        - period: Period number (1-4 for quarters, 5+ for OT)
        - clock: Game clock at time of play
        - score_home, score_away: Current scores
        - description: Description of the play
        - action_type: Type of action (shot, foul, turnover, etc.)
        - team_id, player_id: IDs for team/player involved (when applicable)

    Examples:
        - Get full play-by-play: get_game_playbyplay("0022301148")
        - Get WNBA play-by-play: get_game_playbyplay("0041400406", league="WNBA")
        - Get 4th quarter plays: get_game_playbyplay("0022301148", period=4)
    """
    game = Game(game_id, league=league)
    pbp_df = game.get_playbyplay(standardize=True)

    # Filter by period if specified
    if period is not None:
        # Find period column (could be 'period' or 'PERIOD' depending on standardization)
        period_col = None
        for col in pbp_df.columns:
            if col.lower() == "period":
                period_col = col
                break

        if period_col:
            pbp_df = pbp_df[pbp_df[period_col] == period]

    return cast(list[dict[Any, Any]], pbp_df.to_dict(orient="records"))


def _format_leader(leader: dict) -> dict | None:
    """Format game leader data for output.

    Args:
        leader: Leader dictionary from live scoreboard API

    Returns:
        Formatted leader dict with name and stats, or None if no data
    """
    if not leader or not leader.get("name"):
        return None
    return {
        "name": leader.get("name"),
        "player_id": leader.get("personId"),
        "points": leader.get("points"),
        "rebounds": leader.get("rebounds"),
        "assists": leader.get("assists"),
    }


@mcp.tool()
def get_live_games(
    team_abbreviation: str | None = None,
    include_boxscore: bool = False,
    stat_type: str = "summary",
    league: str = "NBA",
) -> list[dict]:
    """Get live/current NBA or WNBA games with scores and status.

    Returns real-time information about today's games including
    scores, game status, and optionally detailed player statistics.

    Use this tool to answer questions like "What NBA games are on right now?"
    or "What's the score of the Lakers game?"

    Note: Live data availability may vary by league and season.

    Args:
        team_abbreviation: Optional team abbreviation to filter results
            (e.g., "LAL", "BOS", "LVA"). If provided, only returns games
            involving that team.
        include_boxscore: Whether to include detailed player statistics.
            When True, fetches live boxscore data for each game.
            Defaults to False for faster response.
        stat_type: Type of boxscore data to include when include_boxscore=True.
            Options: "summary" (default), "traditional", "advanced", "all".
        league: League to query - "NBA" or "WNBA". Defaults to "NBA".

    Returns:
        List of game dictionaries, each containing:
        - game_id: NBA game identifier
        - game_status: Human-readable status ("In Progress", "Final", "7:00 PM ET")
        - game_status_code: Status integer (1=Scheduled, 2=In Progress, 3=Completed)
        - period: Current period number (if in progress)
        - game_clock: Time remaining in period (if in progress)
        - home_team: {abbreviation, name, score, record}
        - away_team: {abbreviation, name, score, record}
        - game_leaders: Top performers for each team (if available)
        - boxscore: Detailed player stats (if include_boxscore=True)

    Examples:
        - Get all live games: get_live_games()
        - Get Lakers game: get_live_games(team_abbreviation="LAL")
        - Get game with detailed stats: get_live_games(team_abbreviation="BOS", include_boxscore=True)
    """
    from nba_api.live.nba.endpoints import scoreboard

    # Get today's scoreboard
    sb = scoreboard.ScoreBoard()
    data = sb.get_dict()
    games = data.get("scoreboard", {}).get("games", [])

    # Filter by team if specified
    if team_abbreviation:
        team_upper = team_abbreviation.upper()
        games = [
            g
            for g in games
            if g.get("homeTeam", {}).get("teamTricode") == team_upper
            or g.get("awayTeam", {}).get("teamTricode") == team_upper
        ]

    results = []
    for game in games:
        home_team = game.get("homeTeam", {})
        away_team = game.get("awayTeam", {})

        game_dict: dict[str, Any] = {
            "game_id": game.get("gameId"),
            "game_status": game.get("gameStatusText", ""),
            "game_status_code": game.get("gameStatus"),
            "period": game.get("period"),
            "game_clock": game.get("gameClock"),
            "home_team": {
                "abbreviation": home_team.get("teamTricode"),
                "name": f"{home_team.get('teamCity')} {home_team.get('teamName')}",
                "score": home_team.get("score"),
                "record": f"{home_team.get('wins')}-{home_team.get('losses')}",
            },
            "away_team": {
                "abbreviation": away_team.get("teamTricode"),
                "name": f"{away_team.get('teamCity')} {away_team.get('teamName')}",
                "score": away_team.get("score"),
                "record": f"{away_team.get('wins')}-{away_team.get('losses')}",
            },
        }

        # Add game leaders if available
        leaders = game.get("gameLeaders", {})
        if leaders:
            game_dict["game_leaders"] = {
                "home": _format_leader(leaders.get("homeLeaders", {})),
                "away": _format_leader(leaders.get("awayLeaders", {})),
            }

        # Add boxscore if requested
        if include_boxscore and game.get("gameId"):
            try:
                game_obj = Game(game["gameId"], league=league)
                boxscore_dfs = game_obj.get_live_boxscore(stat_type=stat_type)
                game_dict["boxscore"] = [
                    df.to_dict(orient="records") for df in boxscore_dfs
                ]
            except Exception:
                game_dict["boxscore"] = None

        results.append(game_dict)

    return results
