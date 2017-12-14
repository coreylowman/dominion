# Dominion

[Dominion](http://wiki.dominionstrategy.com/index.php/Main_Page) is a deck-building card board game. This is an implementation of the Dominion game for use as a testbed for
developing AI using reinforcement learning. Features so far:

1. Base game fully implemented
1. Simple AI developing interface
1. Server to serve a webpage to play against AI
1. Script to run two AI's against one another and see stats about them.

# Installing

1. Run `pip install -r requirements.txt`
1. Profit

# Source code overview

* `dominion/` contains all the python sources for Dominion
    * `ai/` contains various dominion AI
    * `cards/` contains the implementation of all the cards
    * `effects/` contains the effects that the cards use when they are played
    * `player/` contains player handlers. E.g. ConsolePlayer, WebsocketPlayer, AIPlayer, etc.
    * `game.py` implements the Game class, which manages players, the turns, win conditions, etc.
    * `premade_games.py` defines some of the premade kingdom card sets. 
* `static/` contains web resources that are served when running `dominion_server.py`
* `tests/` contains tests :)
* `dominion_server.py` Starts a server that servers up the web frontend for playing a game.
* `play_local_game.py` Runs a game through a console.
* `run_ai_games.py` Runs many games pitting two AI against each other to see which one is better.
