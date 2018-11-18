import argparse
from dominion import *
import dominion_ai
from collections import defaultdict
import datetime

parser = argparse.ArgumentParser()
parser.add_argument('player1', help='AI to use')
parser.add_argument('player2', help='AI to use')
parser.add_argument('--num_games', default=1000, type=int, help='number of games to run')
args = parser.parse_args()

ai_for_player = {'Player1': args.player1, 'Player2': args.player2}

draw_reasons = defaultdict(int)
wins_for_player = {'Player1': 0, 'Player2': 0}
vp_for_player = {'Player1': [], 'Player2': []}
game_turn_lengths = []
game_times = []
win_reasons_for_player = {'Player1': defaultdict(int), 'Player2': defaultdict(int)}
cards_for_player = {'Player1': defaultdict(int), 'Player2': defaultdict(int)}
games_with_card = defaultdict(int)

player1 = getattr(dominion_ai, args.player1)('Player1')
player2 = getattr(dominion_ai, args.player2)('Player2')

for i in range(args.num_games):
    player1.reset()
    player2.reset()

    # game = make_random_game(player1, player2, set(player1.requires() + player2.requires()))
    game = make_premade_game(player1, player2, 'Size Distortion')

    for card_name in game.card_piles_by_name:
        games_with_card[card_name] += 1

    start_time = datetime.datetime.now()

    game.start()
    while not game.is_over():
        game.run_next_phase()

    end_time = datetime.datetime.now()

    if not game.is_draw():
        wins_for_player[game.winner()] += 1
        win_reasons_for_player[game.winner()][game.finish_reason()] += 1
    else:
        draw_reasons[game.finish_reason()] += 1

    points = game.victory_points_by_player()
    for player in points:
        vp_for_player[player].append(points[player])
    game_turn_lengths.append(game.turn_number)
    game_times.append(end_time - start_time)

    for handle in game.player_handles:
        for card in game.cards_of(handle):
            cards_for_player[handle.name][card.name] += 1

    print(i, wins_for_player)

print('Draws: {}'.format(sum(draw_reasons.values())))
print('Draw reasons: {}'.format(dict(draw_reasons)))
print('Avg game turn length: {}'.format(sum(game_turn_lengths) / len(game_turn_lengths)))
print('Avg game time: {}'.format(sum(game_times, datetime.timedelta(0)) / len(game_times)))
print()

won_games = args.num_games - sum(draw_reasons.values())

for player in sorted(wins_for_player, key=wins_for_player.get, reverse=True):
    for card in cards_for_player[player]:
        cards_for_player[player][card] /= games_with_card[card]

    print('{} stats'.format(ai_for_player[player]))
    print('\tWins: {} ({:.2f}%)'.format(wins_for_player[player], 100.0 * wins_for_player[player] / args.num_games))
    print('\tWin reasons: {}'.format(dict(win_reasons_for_player[player])))
    print('\tAvg points per game: {}'.format(sum(vp_for_player[player]) / len(vp_for_player[player])))
    print('\tCards: {}'.format(sorted(cards_for_player[player].items(), key=lambda q: q[0])))
