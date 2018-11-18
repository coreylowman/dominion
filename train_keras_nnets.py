from dominion import *
from dominion_ai import *
import datetime
from keras.models import load_model
import os


def sign(a):
    return (a > 0) - (a < 0)


def run_game(game):
    try:
        game.start()
        while not game.is_over() and game.turn_number < 100:
            game.run_next_phase()
    except:
        print(game.history)
        for handle in game.player_handles:
            print(handle.name, game.player_state_by_handle[handle])
        raise


def test_against_bm(model, amount_trained, best_wins, num_games=400, save_best=True, name='NNet'):
    draw_reasons = defaultdict(int)
    wins_for_player = {name: 0, 'BM': 0}
    vp_for_player = {name: [], 'BM': []}
    rewards_for_player = {name: [], 'BM': [0]}
    game_turn_lengths = []
    game_times = []
    win_reasons_for_player = {name: defaultdict(int), 'BM': defaultdict(int)}
    cards_for_player = {name: defaultdict(int), 'BM': defaultdict(int)}
    games_with_card = defaultdict(int)

    for i in range(num_games):
        player1 = NNetTrainingPlayer(name, model, epsilon=0.0)
        player2 = BigMoneyPlayer('BM')

        # game = make_random_game(player1, player2, set())
        game = make_premade_game(player1, player2, 'Size Distortion')

        for card_name in game.card_piles_by_name:
            games_with_card[card_name] += 1

        start_time = datetime.datetime.now()
        run_game(game)
        end_time = datetime.datetime.now()

        if not game.is_draw():
            wins_for_player[game.winner()] += 1
            win_reasons_for_player[game.winner()][game.finish_reason()] += 1
        else:
            draw_reasons[game.finish_reason()] += 1

        for handle in game.player_handles:
            for card in game.cards_of(handle):
                cards_for_player[handle.name][card.name] += 1

        points = game.victory_points_by_player()
        for player in points:
            vp_for_player[player].append(points[player])
        rewards_for_player[name].append(sum(map(lambda moment: moment[-2], player1.history)))
        game_turn_lengths.append(game.turn_number)
        game_times.append(end_time - start_time)

    draws = sum(draw_reasons.values())

    info = [
        '\n',
        str(datetime.datetime.now()),
        'Amount trained: {} games'.format(amount_trained),
        'Draws: {} ({:.2f}%)\t{}'.format(draws, 100.0 * draws / num_games, dict(draw_reasons)),
        'Avg length:\t{} turns\t{}'.format(sum(game_turn_lengths) / len(game_turn_lengths),
                                           sum(game_times, datetime.timedelta(0)) / len(game_times)),
    ]

    for player in sorted(wins_for_player):
        for card in cards_for_player[player]:
            cards_for_player[player][card] /= games_with_card[card]
        info.append('{}:\t{} wins ({:.2f}%)\t{}\t{}\t{}'.format(
            player, wins_for_player[player], 100.0 * wins_for_player[player] / num_games,
            dict(win_reasons_for_player[player]), sum(vp_for_player[player]) / len(vp_for_player[player]),
            sorted(cards_for_player[player].items(), key=lambda q: q[0])))
    info.append('')

    print('\n'.join(info))
    with open('stats.txt', 'a') as fp:
        fp.write('\n'.join(info))

    if save_best and wins_for_player[name] > best_wins:
        best_wins = wins_for_player[name]
        model.save('best_{}_{}.hd5'.format(wins_for_player[name], amount_trained))

    return best_wins


def main():
    path = './model.hd5'
    if os.path.exists(path):
        model = load_model(path)
    else:
        model = build_model()

    discount_factor = 1.0
    epsilon = 0.25

    num_completed_games = 0
    best_wins = 0

    self_play_size = 1000

    # best_wins = test_against_bm(model, num_completed_games, best_wins)
    # model.save(path)

    while True:
        input_data = []
        target_values = []
        target_probs = []

        for _ in range(self_play_size):
            num_completed_games += 1

            player1 = NNetTrainingPlayer('Player1', model, epsilon=epsilon)
            player2 = NNetTrainingPlayer('Player2', model, epsilon=epsilon)

            # game = make_random_game(player1, player2, set())
            game = make_premade_game(player1, player2, 'Size Distortion')

            run_game(game)
            points = game.victory_points_by_player()
            is_winner = {
                'Player1': sign(points['Player1'] - points['Player2']),
                'Player2': sign(points['Player2'] - points['Player1']),
            }

            print('\rGame {}: {} turns, {}: {}\t{}\t{}'.format(num_completed_games, game.turn_number,
                                                               game.finish_reason(), game.empty_piles(), points,
                                                               len(input_data)), end='', flush=True)

            for history, name in [(player1.history, 'Player1'), (player2.history, 'Player2')]:
                reward = 1 if is_winner[name] == 1 else 0
                for t, (features, values, winning_prob, actions, chosen_action, r, next_values) in enumerate(history):
                    action_values = values.copy()

                    for i, choice in enumerate(ALL_POSSIBLE_ACTIONS):
                        if choice not in actions:
                            action_values[i] = 0

                    i = ALL_POSSIBLE_ACTIONS.index(chosen_action)
                    next_v = 0 if t + 1 == len(history) else max(next_values)
                    action_values[i] = reward + discount_factor * next_v

                    input_data.append(features)
                    target_values.append(action_values)
                    target_probs.append(is_winner[name])

        print()
        model.fit(x=numpy.array(input_data),
                  y=[numpy.array(target_values), numpy.array(target_probs)],
                  verbose=2, batch_size=2048, epochs=5)

        best_wins = test_against_bm(model, num_completed_games, best_wins)
        model.save(path)


if __name__ == '__main__':
    main()
