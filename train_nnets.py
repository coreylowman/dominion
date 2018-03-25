from dominion import *
from dominion_ai import *
import datetime
from keras.models import load_model
import os

log_fp = open('current.log', 'a')


def sign(a):
    return (a > 0) - (a < 0)


def run_game(game):
    try:
        game.start()
        while not game.is_over():
            game.run_next_phase()
    except:
        print(game.history)
        for handle in game.player_handles:
            print(handle.name, game.player_state_by_handle[handle])
        raise


def test_against_bm(model, num_games=100):
    draw_reasons = defaultdict(int)
    wins_for_player = {'NNet': 0, 'BM': 0}
    vp_for_player = {'NNet': [], 'BM': []}
    game_turn_lengths = []
    game_times = []
    win_reasons_for_player = {'NNet': defaultdict(int), 'BM': defaultdict(int)}
    cards_for_player = {'NNet': defaultdict(int), 'BM': defaultdict(int)}

    for i in range(num_games):
        player1 = NNetTrainingPlayer('NNet', model, epsilon=0.0, use_noise=False)
        player2 = BigMoneyPlayer('BM')

        game = make_premade_game(player1, player2, 'First Game')
        # game = make_random_game(player1, player2, set())

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
        game_turn_lengths.append(game.turn_number)
        game_times.append(end_time - start_time)

    won_games = num_games - sum(draw_reasons.values())

    info = [
        'Draws: {} {}'.format(sum(draw_reasons.values()), dict(draw_reasons)),
        'Avg length:\t{} turns\t{}'.format(sum(game_turn_lengths) / len(game_turn_lengths),
                                           sum(game_times, datetime.timedelta(0)) / len(game_times)),
    ]

    for player in sorted(wins_for_player):
        for card in cards_for_player[player]:
            cards_for_player[player][card] //= num_games
        info.append('{}:\t{} wins ({:.2f}%)\t{}\t{}\t{}'.format(
            player, wins_for_player[player], 100.0 * wins_for_player[player] / won_games,
            dict(win_reasons_for_player[player]), sum(vp_for_player[player]) / len(vp_for_player[player]),
            sorted(cards_for_player[player].items(), key=lambda q: q[0])))
    info.append('')

    log_fp.write('\n'.join(info))
    print('\n'.join(info))


def main():
    path = './model.hd5'
    if os.path.exists(path):
        model = load_model(path)
    else:
        model = build_model()

    discount_factor = 1.0
    epsilon = 0.25

    num_games = 0
    batch_size = 1000

    test_against_bm(model)
    model.save(path)

    while True:
        input_data = []
        target_values = []
        target_probs = []

        avg_values = [0] * len(ALL_POSSIBLE_ACTIONS)

        def collect(vs):
            for i in range(len(avg_values)):
                avg_values[i] += vs[i]

        for _ in range(batch_size):
            num_games += 1

            player1 = NNetTrainingPlayer('Player1', model, epsilon=epsilon, use_noise=True)
            player2 = NNetTrainingPlayer('Player2', model, epsilon=epsilon, use_noise=True)

            game = make_premade_game(player1, player2, 'First Game')
            # game = make_random_game(player1, player2, set())

            run_game(game)
            points = game.victory_points_by_player()
            rewards = {
                'Player1': points['Player1'] - game.turn_number,
                'Player2': points['Player2'] - game.turn_number,
            }

            print('\rGame {}: {} turns, {}: {}\t{}\t{}'.format(num_games, game.turn_number, game.finish_reason(),
                                                               game.empty_piles(), points, rewards), end='', flush=True)

            for history, r in [(player1.history, rewards['Player1']), (player2.history, rewards['Player2'])]:
                for t, (features, values, winning_prob, actual_choices, chosen_action) in enumerate(history):
                    input_data.append(features)

                    all_choices = list(ALL_CARD_NAMES)
                    all_choices.append(None)

                    card_values = values.copy()
                    collect(values)

                    for i, choice in enumerate(all_choices):
                        if choice not in actual_choices:
                            card_values[i] = 0

                    i = all_choices.index(chosen_action)
                    next_v = 0 if t + 1 == len(history) else max(history[t + 1][1])
                    card_values[i] = (r + discount_factor * next_v)

                    target_values.append(card_values)
                    target_probs.append(sign(r))

        print()
        print({ALL_POSSIBLE_ACTIONS[i]: avg_values[i] / len(input_data) for i in range(len(ALL_POSSIBLE_ACTIONS))})

        model.fit(x=numpy.array(input_data),
                  y=[numpy.array(target_values), numpy.array(target_probs)],
                  verbose=2)

        test_against_bm(model)
        model.save(path)


if __name__ == '__main__':
    main()
