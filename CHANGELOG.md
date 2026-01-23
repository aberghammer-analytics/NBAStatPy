# Changelog

## [0.5.0](https://github.com/aberghammer-analytics/NBAStatPy/compare/nbastatpy-v0.4.1...nbastatpy-v0.5.0) (2026-01-23)


### Features

* Add 6 new MCP tools, validation, and bug fixes ([#17](https://github.com/aberghammer-analytics/NBAStatPy/issues/17)) ([d44acae](https://github.com/aberghammer-analytics/NBAStatPy/commit/d44acaec705312fee39b21d7e3c02b1215f4e257))
* add data standardization and validation ([c5fc869](https://github.com/aberghammer-analytics/NBAStatPy/commit/c5fc869530964dec63bf7052d3fe645957642362))
* Add MCP integration for AI-powered NBA data access ([#13](https://github.com/aberghammer-analytics/NBAStatPy/issues/13)) ([388fa33](https://github.com/aberghammer-analytics/NBAStatPy/commit/388fa331983103cd159e4073fba865bc522bd97b))
* simplify MCP server entry point to 'nbastatpy' ([#16](https://github.com/aberghammer-analytics/NBAStatPy/issues/16)) ([ee86c31](https://github.com/aberghammer-analytics/NBAStatPy/commit/ee86c31ff56ce5980e4ba7406af9c58a22069af9))
* update release ([b10f99b](https://github.com/aberghammer-analytics/NBAStatPy/commit/b10f99bc3e107b796f9d9591961021fee7f2e12d))


### Bug Fixes

* correct nba_api parameter names for WNBA support ([#19](https://github.com/aberghammer-analytics/NBAStatPy/issues/19)) ([d1fc963](https://github.com/aberghammer-analytics/NBAStatPy/commit/d1fc963cdf7a53cc93a084769d8b0a8a806bc4bd))
* Remove tests from publish workflow to avoid NBA API timeouts ([4909c30](https://github.com/aberghammer-analytics/NBAStatPy/commit/4909c304dfa4f800340c3b3e3937bfb43c5d3c9c))

## [0.4.1](https://github.com/aberghammer-analytics/NBAStatPy/compare/nbastatpy-v0.4.0...nbastatpy-v0.4.1) (2026-01-20)


### Features

* Add 6 new MCP tools: get_player_info, get_team_roster, get_game_boxscore, get_game_playbyplay, get_league_player_stats, get_league_team_stats
* Add input validation with descriptive error messages via Validators class
* Add RateLimiter class for centralized API rate limiting
* Add _get_player_teams_for_season() helper to reduce code duplication
* Modernize type hints to Python 3.10+ syntax


### Bug Fixes

* Fix undefined variable `team.id` → `self.id` in team.py get_player_onoff()
* Fix undefined `cols` variable in player.py get_salary()

## [0.4.0](https://github.com/aberghammer-analytics/NBAStatPy/compare/nbastatpy-v0.3.0...nbastatpy-v0.4.0) (2026-01-20)


### Features

* simplify MCP server entry point to 'nbastatpy' ([#16](https://github.com/aberghammer-analytics/NBAStatPy/issues/16)) ([ee86c31](https://github.com/aberghammer-analytics/NBAStatPy/commit/ee86c31ff56ce5980e4ba7406af9c58a22069af9))


### Bug Fixes

* Remove tests from publish workflow to avoid NBA API timeouts ([4909c30](https://github.com/aberghammer-analytics/NBAStatPy/commit/4909c304dfa4f800340c3b3e3937bfb43c5d3c9c))

## [0.3.0](https://github.com/aberghammer-analytics/NBAStatPy/compare/nbastatpy-v0.2.0...nbastatpy-v0.3.0) (2026-01-18)


### Features

* Add MCP integration for AI-powered NBA data access ([#13](https://github.com/aberghammer-analytics/NBAStatPy/issues/13)) ([388fa33](https://github.com/aberghammer-analytics/NBAStatPy/commit/388fa331983103cd159e4073fba865bc522bd97b))

## [0.2.0](https://github.com/aberghammer-analytics/NBAStatPy/compare/nbastatpy-v0.1.8...nbastatpy-v0.2.0) (2025-10-05)


### Features

* add data standardization and validation ([c5fc869](https://github.com/aberghammer-analytics/NBAStatPy/commit/c5fc869530964dec63bf7052d3fe645957642362))
* update release ([b10f99b](https://github.com/aberghammer-analytics/NBAStatPy/commit/b10f99bc3e107b796f9d9591961021fee7f2e12d))
