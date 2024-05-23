# NBAStatPy

## Overview

This is an easy-to-use wrapper for the `nba_api` package. The goal is to be able to easily access and find data for a player, game, team, or season. 

The data is accessed through a class based on how you're searching for it. A quickstart example is shown below. Currently there are 4 classes:

- `Game`
- `Player`
- `Season`
- `Team`

## Quickstart

To get started you can import the class that represents the data you're searching for.

```{python}
from nbastatpy.player import Player
```

Then you build a player using either an ID from stats.nba.com or the player's name. When you're building the player object you can add additional search data like season, data format, or playoffs vs. regular season.

```{python}
player = Player(
    "Giannis", 
    season="2020", 
    playoffs=True,
    permode="PerGame"
)
```

