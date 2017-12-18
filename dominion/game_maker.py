from .cards import *
from .game import Game
import random

PREMADE_GAMES = {
    'Deck Top': [artisan, bureaucrat, council_room, festival, harbinger, laboratory, moneylender, sentry, vassal,
                 village],
    'First Game': [cellar, market, merchant, militia, mine, moat, remodel, smithy, village, workshop],
    'Improvements': [artisan, cellar, market, merchant, mine, moat, moneylender, poacher, remodel, witch],
    'Silver & Gold': [bandit, bureaucrat, chapel, harbinger, laboratory, merchant, mine, moneylender, throne_room,
                      vassal],
    'Size Distortion': [artisan, bandit, bureaucrat, chapel, festival, gardens, sentry, throne_room, witch,
                        workshop],
    'Sleight of Hand': [cellar, council_room, festival, gardens, harbinger, library, militia, poacher, smithy,
                        throne_room],
}


def make_premade_game(player1, player2, game_name):
    game = Game(PREMADE_GAMES[game_name])

    game.add_player(player1)
    game.add_player(player2)

    return game


def make_random_game(player1, player2, requires):
    possible_choices = set(DOMINION_CARDS)

    kingdom_cards = set()
    kingdom_cards.update(requires)

    # remove all the cards already in kingdom_cards from the choices
    possible_choices.difference_update(kingdom_cards)

    kingdom_cards.update(random.sample(possible_choices, 10 - len(kingdom_cards)))

    game = Game(kingdom_cards)

    game.add_player(player1)
    game.add_player(player2)

    return game
