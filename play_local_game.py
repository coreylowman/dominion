import argparse
from dominion import *

parser = argparse.ArgumentParser()
parser.add_argument('game', choices=PREMADE_GAMES.keys(), default='First Game', help='Set of kingdom cards to use')
args = parser.parse_args()

game = Game(PREMADE_GAMES[args.game])

game.add_player(ConsolePlayer())
game.add_player(BigMoneyPlayer('BigMoneyPlayer'))

game.start()
while not game.is_over():
    game.run_next_phase()
