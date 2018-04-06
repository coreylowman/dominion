from dominion import AIPlayer, ALL_CARD_NAMES, LocalPlayerHandle
from keras import Model
from keras.layers import Input, Dense
from keras.models import load_model
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


class NNetFeatures_v1(LocalPlayerHandle):
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
            inputs.append(self.cards_in_deck.get(card, 0))
            inputs.append(self.cards_in_discard.get(card, 0))
            inputs.append(self.hand.get(card, 0))
            inputs.append(self.cards_in_play_area.get(card, 0))
            inputs.append(self.num_left_of.get(card, 0))
            inputs.append(int(self.last_card_played is not None and self.last_card_played == card))
        return inputs


class NNetTrainingPlayer(AIPlayer, NNetFeatures_v1):
    def __init__(self, name, model, epsilon):
        super().__init__(name)

        self.model = model
        self.history = []
        self.waiting_for_next_values = []
        self.epsilon = epsilon

    def predict(self):
        features = self.get_features()
        _values, _winning_prob = self.model.predict(numpy.array([features]))

        values = _values[0]
        winning_prob = _winning_prob[0]

        score_by_action = {}
        for i, card in enumerate(ALL_POSSIBLE_ACTIONS):
            score_by_action[card] = values[i]

        return score_by_action, features, values, winning_prob

    def _record(self, moment):
        if len(self.waiting_for_next_values) > 0:
            for h in self.waiting_for_next_values:
                h.append(moment[1])
            self.history.extend(self.waiting_for_next_values)
            self.waiting_for_next_values.clear()

        self.waiting_for_next_values.append(moment)

    def choose_action(self, actions, score_by_action):
        if random.uniform(0, 1) <= self.epsilon:
            return random.choice(actions)
        else:
            return max(actions, key=score_by_action.get)

    def action_phase(self):
        while self.can_play_anything():
            score_by_action, features, values, winning_prob = self.predict()

            actions = self.cards_can_play()
            actions.append(None)
            action = self.choose_action(actions, score_by_action)

            if action is not None:
                reward = self.play(action)
            else:
                reward = 0

            self._record([features, values, winning_prob, actions, action, reward])

            if action is None:
                break

    def buy_phase(self):
        while self.can_buy_anything():
            score_by_action, features, values, winning_prob = self.predict()

            actions = self.cards_can_buy()
            actions.append(None)
            action = self.choose_action(actions, score_by_action)

            if action is not None:
                reward = self.buy(action)
            else:
                reward = 0

            self._record([features, values, winning_prob, actions, action, reward])

            if action is None:
                break

    def choose_card_from(self, collection):
        score_by_action, features, values, winning_prob = self.predict()

        actions = collection
        action = self.choose_action(actions, score_by_action)

        reward = 0

        self.waiting_for_next_values.append([features, values, winning_prob, actions, action, reward])

        return action

    def ask_yes_or_no(self, prompt):
        score_by_action, features, values, winning_prob = self.predict()

        actions = list(ALL_POSSIBLE_ACTIONS)
        action = self.choose_action(actions, score_by_action)

        reward = 0

        self.waiting_for_next_values.append([features, values, winning_prob, actions, action, reward])

        return action is not None


class ModelPlayer(AIPlayer, NNetFeatures_v1):
    def __init__(self, name):
        super().__init__(name)

        self.model = load_model(self.get_path())

    def get_path(self):
        return None

    def predict(self):
        features = self.get_features()
        _values, _winning_prob = self.model.predict(numpy.array([features]))

        winning_prob = _winning_prob[0]
        score_by_action = {}
        for i, card in enumerate(ALL_POSSIBLE_ACTIONS):
            score_by_action[card] = _values[0][i]
        return score_by_action, winning_prob

    def choose_action(self, actions):
        score_by_action, _ = self.predict()
        return max(actions, key=score_by_action.get)

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


class FirstGameNNet(ModelPlayer):
    def get_path(self):
        return './models/first_game_917000.hd5'


class NNetDifficulty1(ModelPlayer):
    def get_path(self):
        return './models/all_11_119000.hd5'


class NNetDifficulty2(ModelPlayer):
    def get_path(self):
        return './models/all_59_188000.hd5'


class NNetDifficulty3(ModelPlayer):
    def get_path(self):
        return './models/all_107_197000.hd5'


class NNetDifficulty4(ModelPlayer):
    def get_path(self):
        return './models/all_152_207000.hd5'


class NNetDifficulty5(ModelPlayer):
    def get_path(self):
        return './models/all_221_213000.hd5'


class NNetDifficulty6(ModelPlayer):
    def get_path(self):
        return './models/all_265_288000.hd5'


class NNetDifficulty7(ModelPlayer):
    def get_path(self):
        return './models/all_303_311000.hd5'


class NNetDifficulty8(ModelPlayer):
    def get_path(self):
        return './models/all_319_345000.hd5'
