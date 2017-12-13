import argparse
from dominion import *
import dominion.ai
from collections import defaultdict
import datetime

parser = argparse.ArgumentParser()
parser.add_argument('player1', help='AI to use')
parser.add_argument('player2', help='AI to use')
parser.add_argument('num_games', default=1000, type=int, help='number of games to run')
args = parser.parse_args()

ai_for_player = {'Player1': args.player1, 'Player2': args.player2}

num_draws = 0
wins_for_player = {'Player1': 0, 'Player2': 0}
vp_for_player = {'Player1': [], 'Player2': []}
game_turn_lengths = []
game_times = []
win_reasons_for_player = {'Player1': defaultdict(int), 'Player2': defaultdict(int)}

for i in range(args.num_games):
    player1 = getattr(dominion.ai, args.player1)('Player1')
    player2 = getattr(dominion.ai, args.player2)('Player2')

    cards = random.sample(DOMINION_CARDS, 10)

    required_cards = set()
    required_cards.update(player1.requires())
    required_cards.update(player2.requires())

    for required_card in required_cards:
        if required_card not in cards:
            cards[random.choice(range(10))] = required_card

    game = Game(cards)

    game.add_player(player1)
    game.add_player(player2)

    start_time = datetime.datetime.now()

    game.start()
    while not game.is_over():
        game.run_next_phase()

    end_time = datetime.datetime.now()

    if not game.is_draw():
        wins_for_player[game.winner()] += 1
        win_reasons_for_player[game.winner()][game.finish_reason()] += 1
    else:
        num_draws += 1

    points = game.victory_points_by_player()
    for player in points:
        vp_for_player[player].append(points[player])
    game_turn_lengths.append(game.turn_number)
    game_times.append(end_time - start_time)

print('Draws: {}'.format(num_draws))
print('Avg game turn length: {}'.format(sum(game_turn_lengths) / len(game_turn_lengths)))
print('Avg game time: {}'.format(sum(game_times, datetime.timedelta(0)) / len(game_times)))
print()

for player in sorted(wins_for_player, key=wins_for_player.get, reverse=True):
    print('{} stats'.format(ai_for_player[player]))
    print('\tWins: {}'.format(wins_for_player[player]))
    print('\tWin reasons: {}'.format(dict(win_reasons_for_player[player])))
    print('\tAvg points per game: {}'.format(sum(vp_for_player[player]) / len(vp_for_player[player])))
