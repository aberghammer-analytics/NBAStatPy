from typing import Dict, List, Set


class ColumnTypes:
    """Standard column type mappings for common NBA data fields."""

    # Numeric types
    INTEGER_COLUMNS: Set[str] = {
        "age",
        "games",
        "games_played",
        "gp",
        "w",
        "l",
        "wins",
        "losses",
        "season_year",
        "draft_year",
        "draft_round",
        "draft_number",
        "fgm",
        "fga",
        "fg3m",
        "fg3a",
        "ftm",
        "fta",
        "oreb",
        "dreb",
        "reb",
        "ast",
        "stl",
        "blk",
        "tov",
        "pf",
        "pts",
        "plus_minus",
    }

    FLOAT_COLUMNS: Set[str] = {
        "fg_pct",
        "fg3_pct",
        "ft_pct",
        "min",
        "minutes",
        "height_inches",
        "weight",
        "ts_pct",
        "efg_pct",
        "ast_pct",
        "reb_pct",
        "usg_pct",
        "pace",
        "pie",
    }

    # String types
    STRING_COLUMNS: Set[str] = {
        "player_name",
        "team_name",
        "team_abbreviation",
        "matchup",
        "wl",
        "player_first_name",
        "player_last_name",
        "position",
        "college",
        "country",
    }


class IDFields:
    """Registry of ID fields and their standardization rules."""

    # Fields that should be zero-padded to 10 digits
    ID_FIELDS: Set[str] = {
        "player_id",
        "team_id",
        "game_id",
        "person_id",
        "playerid",
        "teamid",
        "gameid",
        "personid",
    }

    # Mapping of inconsistent ID field names to standardized names
    ID_FIELD_MAPPING: Dict[str, str] = {
        "gameid": "game_id",
        "teamid": "team_id",
        "playerid": "player_id",
        "person_id": "player_id",
        "personid": "player_id",
    }


class DateFields:
    """Registry of date fields and parsing formats."""

    # Fields that should be parsed as dates
    DATE_FIELDS: Set[str] = {
        "game_date",
        "birthdate",
        "birth_date",
        "from_year",
        "to_year",
    }

    # Date parsing formats to try (in order)
    DATE_FORMATS: List[str] = [
        "%Y-%m-%dT%H:%M:%S",  # ISO with time
        "%Y-%m-%d",  # ISO date
        "%m/%d/%Y",  # US format
        "%d/%m/%Y",  # International format
    ]


class TimeFields:
    """Registry of time fields that need conversion."""

    # Fields in MM:SS format that should be converted to seconds
    MINUTES_SECONDS_FIELDS: Set[str] = {
        "min",
        "minutes",
        "matchupminutes",
    }

    # Fields that represent seconds already
    SECONDS_FIELDS: Set[str] = {
        "seconds",
        "matchup_seconds",
        "clock_seconds",
    }


class SpecialFields:
    """Special field handling rules."""

    # Fields that indicate playoff vs regular season
    PLAYOFF_INDICATORS: Set[str] = {
        "season_type",
        "season_type_all_star",
        "is_playoffs",
    }

    # Height fields (in feet-inches format like "6-11")
    HEIGHT_FIELDS: Set[str] = {
        "height",
        "player_height",
    }

    # Fields that should be added during standardization
    METADATA_FIELDS: Set[str] = {
        "standardized_at",
        "source_endpoint",
    }


class TableConfigs:
    """Table-specific configuration rules."""

    # Player endpoints that return player data
    PLAYER_ENDPOINTS: Set[str] = {
        "commonplayerinfo",
        "playercareerstats",
        "playerdashboardbygeneralsplits",
        "playerdashboardbygamesplits",
        "playerdashboardbyshootingsplits",
        "playerawards",
        "playergamelog",
        "draftcombinestats",
    }

    # Game endpoints
    GAME_ENDPOINTS: Set[str] = {
        "boxscoretraditionalv3",
        "boxscoreadvancedv3",
        "boxscoredefensivev2",
        "boxscorefourfactorsv3",
        "boxscorehustlev2",
        "boxscorematchupsv3",
        "boxscoremiscv3",
        "boxscorescoringv3",
        "boxscoreusagev3",
        "boxscoreplayertrackv3",
        "gamerotation",
        "playbyplayv3",
        "winprobabilitypbp",
    }

    # Season endpoints
    SEASON_ENDPOINTS: Set[str] = {
        "leaguedashlineups",
        "leaguelineupviz",
        "leaguedashopppptshot",
        "leaguedashplayerclutch",
        "leaguedashplayerptshot",
        "leaguedashplayershotlocations",
        "leaguedashplayerstats",
        "leaguedashteamclutch",
        "leaguedashteamptshot",
        "leaguedashteamshotlocations",
        "leaguedashteamstats",
        "playergamelogs",
        "leaguegamelog",
        "leaguehustlestatsplayer",
        "leaguehustlestatsteam",
        "leagueseasonmatchups",
        "playerestimatedmetrics",
        "synergyplaytypes",
        "leaguedashptstats",
        "leaguedashptdefend",
        "leaguedashptteamdefend",
    }

    # Team endpoints
    TEAM_ENDPOINTS: Set[str] = {
        "commonteamroster",
        "teamyearbyyearstats",
        "teamdashboardbygeneralsplits",
        "teamdashboardbyshootingsplits",
        "franchiseleaders",
        "franchiseplayers",
        "teamdashptpass",
        "teamplayeronoffdetails",
    }
