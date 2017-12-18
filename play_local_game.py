import argparse
from dominion import *
import dominion.ai

parser = argparse.ArgumentParser()
parser.add_argument('ai', help='AI to use')
args = parser.parse_args()

ai_player = getattr(dominion.ai, args.ai)(args.ai)
console_player = ConsolePlayer()

game = make_random_game(console_player, ai_player, ai_player.requires())

game.add_player(console_player)
game.add_player(ai_player)

game.start()
while not game.is_over():
    game.run_next_phase()
game.complete()
