from typing import Any, cast

from nbastatpy import League, Team
from nbastatpy.mcp.server import mcp
from nbastatpy.utils import Formatter, PlayTypes, Validators


@mcp.tool()
def get_team_recent_games(
    team_abbreviation: str,
    last_n_games: int = 10,
    season: str | None = None,
    season_type: str = "Regular Season",
    include_opponent_stats: bool = True,
    include_advanced_stats: bool = False,
) -> dict:
    """Get statistics from the last n games for a team.

    Returns game-by-game stats including points, rebounds, assists, shooting percentages,
    and optionally opponent stats and advanced metrics.

    The team's league (NBA or WNBA) is auto-detected from the abbreviation.

    Args:
        team_abbreviation: Team abbreviation (e.g., "MIL", "LAL", "LVA" for Las Vegas Aces).
        last_n_games: Number of recent games to retrieve (1-82). Defaults to 10.
        season: Season year (e.g., "2024", "2024-25"). Defaults to current season.
        season_type: "Regular Season" or "Playoffs". Defaults to "Regular Season".
        include_opponent_stats: Whether to include opponent stats for each game (OPP_PTS, OPP_REB, etc.). Defaults to True.
        include_advanced_stats: Whether to include advanced stats (OFF_RATING, DEF_RATING, NET_RATING, PACE, EFG_PCT, TS_PCT, PIE, FT_RATE, TOV_PCT, OREB_PCT). Slower due to additional API calls. Defaults to False.
    """
    # Validate parameters
    Validators.validate_team_abbreviation(team_abbreviation)
    Validators.validate_last_n_games(last_n_games)
    Validators.validate_season_type(season_type)

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

    return {
        "league": team.league,
        "team_name": team.full_name,
        "team_id": team.id,
        "team_abbreviation": team.abbreviation,
        "games": cast(list[dict[Any, Any]], game_log.to_dict(orient="records")),
    }


@mcp.tool()
def get_team_play_type_stats(
    play_type: str = "all",
    team_name: str | None = None,
    offensive: bool = True,
    season: str | None = None,
    per_mode: str = "PerGame",
    season_type: str = "Regular Season",
    league: str = "NBA",
) -> list[dict]:
    """Get NBA or WNBA play type (synergy) statistics for teams.

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
        team_name: Optional team name to filter results (e.g., "Lakers", "Aces").
            Uses case-insensitive partial matching. If not provided, returns all teams.
        offensive: True for offensive stats, False for defensive. Defaults to True.
        season: Season year (e.g., "2024", "2024-25"). Defaults to current season.
        per_mode: "PerGame" or "Totals". Defaults to "PerGame".
        season_type: "Regular Season" or "Playoffs". Defaults to "Regular Season".
        league: League to query - "NBA" or "WNBA". Defaults to "NBA".

    Examples:
        - Get all isolation stats: get_team_play_type_stats(play_type="Isolation")
        - Get Lakers' play type stats: get_team_play_type_stats(team_name="Lakers")
        - Get WNBA play type stats: get_team_play_type_stats(league="WNBA")
        - Get defensive transition stats: get_team_play_type_stats(play_type="Transition", offensive=False)
    """
    # Validate parameters
    Validators.validate_season_type(season_type)

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
    league_obj = League(
        season_year=season_year,
        playoffs=playoffs,
        permode=normalized_permode,
        league=league,
    )

    # Get synergy team data with standardization
    df = league_obj.get_synergy_team(
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


@mcp.tool()
def get_team_tracking_stats(
    track_type: str = "Efficiency",
    team_name: str | None = None,
    season: str | None = None,
    per_mode: str = "PerGame",
    season_type: str = "Regular Season",
    league: str = "NBA",
) -> list[dict]:
    """Get NBA or WNBA tracking statistics for teams.

    Returns team tracking data including speed/distance, possessions, drives, passing,
    catch-and-shoot, pull-up shots, post touches, paint touches, elbow touches, and more.
    Useful for understanding team movement patterns, ball handling, and efficiency metrics.

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
        team_name: Optional team name to filter results (e.g., "Lakers", "Aces").
            Uses case-insensitive partial matching. If not provided, returns all teams.
        season: Season year (e.g., "2024", "2024-25"). Defaults to current season.
        per_mode: "PerGame" or "Totals". Defaults to "PerGame".
        season_type: "Regular Season" or "Playoffs". Defaults to "Regular Season".
        league: League to query - "NBA" or "WNBA". Defaults to "NBA".

    Examples:
        - Get all team drive stats: get_team_tracking_stats(track_type="Drives")
        - Get Lakers' tracking stats: get_team_tracking_stats(team_name="Lakers")
        - Get WNBA tracking stats: get_team_tracking_stats(league="WNBA")
        - Get all tracking types: get_team_tracking_stats(track_type="all")
    """
    # Validate parameters
    Validators.validate_season_type(season_type)

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
    league_obj = League(
        season_year=season_year,
        playoffs=playoffs,
        permode=normalized_permode,
        league=league,
    )

    # Get tracking team data with standardization
    df = league_obj.get_tracking_team(track_type=track_type, standardize=True)

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


@mcp.tool()
def get_team_roster(
    team_abbreviation: str,
    season: str | None = None,
) -> dict:
    """Get the roster for an NBA or WNBA team.

    Returns the list of players on a team's roster for a given season,
    including player names, positions, jersey numbers, and basic info.

    The team's league (NBA or WNBA) is auto-detected from the abbreviation.

    Args:
        team_abbreviation: Team abbreviation (e.g., "MIL", "LAL", "LVA" for Las Vegas Aces).
        season: Season year (e.g., "2024", "2024-25"). Defaults to current season.

    Returns:
        Dictionary containing:
        - league: "NBA" or "WNBA"
        - team_name, team_id, team_abbreviation: Team identifiers
        - roster: List of roster entries, each containing:
            - player_id: Player ID
            - player: Player name
            - num: Jersey number
            - position: Playing position
            - height: Player height
            - weight: Player weight
            - birth_date: Date of birth
            - age: Player age
            - exp: Years of experience
            - school: College/school attended

    Examples:
        - Get Lakers roster: get_team_roster("LAL")
        - Get Las Vegas Aces roster: get_team_roster("LVA")
        - Get 2023 Bucks roster: get_team_roster("MIL", season="2023")
    """
    # Validate parameters
    Validators.validate_team_abbreviation(team_abbreviation)

    # Normalize season format if provided
    season_year = str(Formatter.normalize_season_year(season)) if season else None

    team = Team(team_abbreviation, season_year=season_year)
    roster_dfs = team.get_roster(standardize=True)

    # Roster data is in the first DataFrame
    roster_list: list[dict[Any, Any]] = []
    if roster_dfs and len(roster_dfs) > 0:
        roster_df = roster_dfs[0]
        roster_list = cast(list[dict[Any, Any]], roster_df.to_dict(orient="records"))

    return {
        "league": team.league,
        "team_name": team.full_name,
        "team_id": team.id,
        "team_abbreviation": team.abbreviation,
        "roster": roster_list,
    }
