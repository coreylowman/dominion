from dominion import AIPlayer, ALL_CARD_NAMES
from keras import Model
from keras.layers import Input, Dense, BatchNormalization
import numpy
import random

# inputs:
# -turn number
# -is my turn
# -is my opponents turn
# -is buy phase
# -is action phase
# -actions
# -buys
# -coins
# for each card:
#   -num in deck
#   -num in discard
#   -num in hand
#   -num in play_area
#   -num in supply
#   -was just played

# outputs:
# for each card:
#   -value
# -should take action
# -prob of winning
NNET_NUM_INPUTS = 8 + 6 * len(ALL_CARD_NAMES)

ALL_POSSIBLE_ACTIONS = list(ALL_CARD_NAMES)
ALL_POSSIBLE_ACTIONS.append(None)


def build_model():
    inputs = Input(shape=(NNET_NUM_INPUTS,))
    x = Dense(NNET_NUM_INPUTS * 2, activation='relu')(inputs)
    x = Dense(NNET_NUM_INPUTS * 2, activation='relu')(x)
    x = Dense(NNET_NUM_INPUTS, activation='relu')(x)
    x = Dense(NNET_NUM_INPUTS, activation='relu')(x)
    card_values = Dense(len(ALL_POSSIBLE_ACTIONS), name='values')(x)

    prob_winning = Dense(1, activation='tanh', name='prob_winning')(inputs)

    model = Model(inputs=inputs, outputs=[card_values, prob_winning])
    model.compile(loss='mean_squared_error', optimizer='adam')
    return model


class NNetTrainingPlayer(AIPlayer):
    def __init__(self, name, model: Model, epsilons, use_noise):
        super().__init__(name)

        self.model = model
        self.history = []
        self.epsilons = epsilons
        self.use_noise = use_noise

    def get_features(self):
        inputs = [
            self.turn_number,
            int(self.my_turn),
            int(not self.my_turn),  # opponents turn
            int(not self.is_action_phase),  # buy phase
            int(self.is_action_phase),  # action phase
            self.actions,
            self.buys,
            self.coins,
        ]
        for card in ALL_CARD_NAMES:
            inputs.append(self._pct_in(self.cards_in_deck, card))
            inputs.append(self._pct_in(self.cards_in_discard, card))
            inputs.append(self._pct_in(self.hand, card))
            inputs.append(self._pct_in(self.cards_in_play_area, card))
            inputs.append(self._pct_in(self.num_left_of, card))
            inputs.append(int(self.last_card_played is not None and self.last_card_played == card))
        return inputs

    def _pct_in(self, collection, card):
        return 0 if card not in collection else collection[card]

    def predict(self):
        features = self.get_features()
        _values, _winning_prob = self.model.predict(numpy.array([features]))
        self.history.append([features, _values[0], _winning_prob[0]])

        if self.use_noise:
            noise = numpy.random.dirichlet([0.03] * len(_values[0]))
        else:
            noise = _values[0].copy()

        winning_prob = _winning_prob[0]
        score_by_action = {}
        for i, card in enumerate(ALL_POSSIBLE_ACTIONS):
            score_by_action[card] = 0.75 * _values[0][i] + 0.25 * noise[i]
        return score_by_action, winning_prob

    def choose_action(self, actions):
        score_by_action, _ = self.predict()

        if random.uniform(0, 1) <= self.epsilons[self.turn_number]:
            action = random.choice(actions)
        else:
            action = max(actions, key=score_by_action.get)

        self.history[-1].append(actions)
        self.history[-1].append(action)

        return action

    def action_phase(self):
        while self.can_play_anything():
            actions = self.cards_can_play()
            actions.append(None)

            action = self.choose_action(actions)
            if action is None:
                break

            self.play(action)

    def buy_phase(self):
        while self.can_buy_anything():
            actions = self.cards_can_buy()
            actions.append(None)

            action = self.choose_action(actions)
            if action is None:
                break

            self.buy(action)

    def choose_card_from(self, collection):
        return self.choose_action(collection)

    def ask_yes_or_no(self, prompt):
        action = self.choose_action(list(ALL_POSSIBLE_ACTIONS))
        return action is not None
