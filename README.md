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

Once you have the player object, you can get different datasets based on the criteria. For instance, you can get the awards the player has won by doing the following:

```{python}
player.get_awards()
```

This returns a pandas dataframe with the awards won by the player each year.

There are a lot of endpoints and various arguments for more complex queries like tracking and synergy datasets.
