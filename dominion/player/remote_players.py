from .player_handle import PlayerHandle
import json
import inspect


class WebsocketPlayer(PlayerHandle):
    def __init__(self, name, websocket):
        super().__init__(name)

        self.websocket = websocket

    def _make_msg(self, fields):
        del fields['self']
        fields['type'] = inspect.stack()[1][3]
        return json.dumps(fields)

    def notify_player_joined(self, player):
        self.websocket.send(self._make_msg(locals()))

    def notify_joined_game(self, supply_piles, card_costs, card_is_action):
        self.websocket.send(self._make_msg(locals()))

    def notify_started_game(self):
        self.websocket.send(self._make_msg(locals()))

    def notify_finished_game(self, game_results):
        self.websocket.send(self._make_msg(locals()))

    def notify_started_action_phase(self, player):
        self.websocket.send(self._make_msg(locals()))

        if player == self.name:
            while True:
                message = json.loads(self.websocket.receive())
                if message['type'] == 'finish_action_phase':
                    break
                elif message['type'] == 'play_card':
                    self.play(message['card'])

            self.finish_action_phase()

    def notify_started_buy_phase(self, player):
        self.websocket.send(self._make_msg(locals()))

        if player == self.name:
            while True:
                message = json.loads(self.websocket.receive())
                if message['type'] == 'finish_turn':
                    break
                elif message['type'] == 'buy_card':
                    self.buy(message['card'])

            self.finish_turn()

    def notify_gained_actions(self, player, amount):
        self.websocket.send(self._make_msg(locals()))

    def notify_gained_buys(self, player, amount):
        self.websocket.send(self._make_msg(locals()))

    def notify_gained_coins(self, player, amount):
        self.websocket.send(self._make_msg(locals()))

    def notify_gained_card_to_hand(self, player, card):
        self.websocket.send(self._make_msg(locals()))

    def notify_gained_card_to_deck(self, player, card):
        self.websocket.send(self._make_msg(locals()))

    def notify_gained_card_to_discard(self, player, card):
        self.websocket.send(self._make_msg(locals()))

    def notify_trashed_card(self, player, card):
        self.websocket.send(self._make_msg(locals()))

    def notify_took_card_from_hand(self, player, card):
        self.websocket.send(self._make_msg(locals()))

    def notify_took_card_from_play_area(self, card):
        self.websocket.send(self._make_msg(locals()))

    def notify_took_card_from_deck(self, card):
        self.websocket.send(self._make_msg(locals()))

    def notify_took_card_from_discard(self, player, card):
        self.websocket.send(self._make_msg(locals()))

    def notify_played_card(self, player, card):
        self.websocket.send(self._make_msg(locals()))

    def notify_card_bought(self, card):
        self.websocket.send(self._make_msg(locals()))

    def choose_card_from(self, collection):
        msg = self._make_msg(locals())

        while True:
            self.websocket.send(msg)

            response = json.loads(self.websocket.receive())
            if 'type' in response and response['type'] == 'chosen_card' \
                    and 'card' in response and response['card'] in collection:
                return response['card']

    def ask_yes_or_no(self, prompt):
        msg = self._make_msg(locals())

        while True:
            self.websocket.send(msg)

            response = json.loads(self.websocket.receive())
            if 'type' in response and response['type'] == 'answer_yes_or_no' and 'answer' in response:
                return response['answer']
