from .cards import *
import random
from enum import Enum, auto


class Phase(Enum):
    ACTION = auto()
    BUY = auto()


class PlayerState:
    def __init__(self, game, handle):
        self.game = game
        self.handle = handle

        self.actions = 0
        self.buys = 0
        self.coins = 0

        self.deck = []
        self.hand = []
        self.play_area = []
        self.discard = []
        self.temp_area = []

    def all_cards(self):
        cards = []
        for collection in [self.deck, self.hand, self.play_area, self.discard, self.temp_area]:
            cards.extend(collection)
        return cards

    def num_cards(self):
        return len(self.all_cards())

    def play_remaining_treasures(self):
        remaining_treasures = list(map(lambda card: card.name, filter(lambda card: card.is_treasure(), self.hand)))
        for card_name in remaining_treasures:
            self.handle.play(card_name)

    def victory_points(self):
        points = 0
        for card in self.all_cards():
            points += card.victory_points.invoke(self.handle, self.game, None)
        return points


class Game:
    def __init__(self, kingdom_card_constructors):
        self.kingdom_cards = list(
            map(lambda constr: constr.__name__, sorted(kingdom_card_constructors, key=lambda constr: constr().cost)))
        self.card_piles_by_name = {}

        for constructor in kingdom_card_constructors:
            self.card_piles_by_name[constructor.__name__] = [constructor() for _ in range(8)]

        default_cards = [(estate, 8), (duchy, 8), (province, 8), (curse, 20), (copper, 46), (silver, 40), (gold, 30)]
        for constructor, amount in default_cards:
            self.card_piles_by_name[constructor.__name__] = [constructor() for _ in range(amount)]

        self.turn_number = 1

        self.current_turn = 0
        self.current_phase = Phase.ACTION

        self.player_handles = []
        self.player_state_by_handle = {}

        self.trash = []

    def add_player(self, player_handle):
        player_handle.join_game(self)

        for handle in self.player_handles:
            player_handle.notify_player_joined(handle.name)
            handle.notify_player_joined(player_handle.name)

        self.player_handles.append(player_handle)
        self.player_state_by_handle[player_handle] = PlayerState(self, player_handle)

    def opponents_of(self, player_handle):
        return list(filter(lambda other: other != player_handle, self.player_state_by_handle))

    def player_has_moat(self, player_handle):
        return any(map(lambda card: card.name == 'moat', self.player_state_by_handle[player_handle].hand))

    def complete(self):
        if not self.is_over():
            raise ValueError('Game::complete() called when game was not over.')

        game_results = {
            'turns': self.turn_number,
            'is_draw': self.is_draw(),
            'winner': '' if self.is_draw() else self.winner(),
            'reason': self.finish_reason(),
        }
        game_results.update(self.victory_points_by_player())

        for handle in self.player_handles:
            handle.notify_finished_game(game_results)

    def is_over(self):
        return self.num_empty_piles() == 3 or len(self.card_piles_by_name['province']) == 0

    def is_draw(self):
        vp_by_player = self.victory_points_by_player()
        player1 = list(vp_by_player.keys())[0]
        return all(map(lambda player: vp_by_player[player] == vp_by_player[player1], vp_by_player))

    def finish_reason(self):
        if self.num_empty_piles() == 3:
            return '3 empty piles'
        else:
            return 'No more provinces'

    def winner(self):
        vp_by_player = self.victory_points_by_player()
        return max(vp_by_player, key=vp_by_player.get)

    def victory_points_by_player(self):
        vp_by_player = {}
        for handle in self.player_handles:
            vp_by_player[handle.name] = self.player_state_by_handle[handle].victory_points()
        return vp_by_player

    def start(self):
        random.shuffle(self.player_handles)

        for handle in self.player_handles:
            handle.notify_started_game()

        for handle, state in self.player_state_by_handle.items():
            state.discard = [copper(), copper(), copper(), copper(), copper(), copper(), copper(), estate(), estate(),
                             estate()]
            self.cleanup_for(handle)

    def run_next_phase(self):
        if self.current_phase == Phase.ACTION:
            self.start_action_phase_for(self.player_handles[self.current_turn])
        else:
            self.start_buy_phase_for(self.player_handles[self.current_turn])

    def is_players_turn(self, player_handle):
        return player_handle == self.player_handles[self.current_turn]

    def start_action_phase_for(self, player_handle):
        i = (self.current_turn + 1) % len(self.player_handles)
        while i != self.current_turn:
            self.player_handles[i].notify_started_action_phase(player_handle.name)
            i = (i + 1) % len(self.player_handles)
        player_handle.notify_started_action_phase(player_handle.name)

    def finish_action_phase_for_player(self, player_handle):
        if not self.is_players_turn(player_handle) or self.current_phase != Phase.ACTION:
            return

        self.player_state_by_handle[player_handle].play_remaining_treasures()

        self.current_phase = Phase.BUY

    def start_buy_phase_for(self, player_handle):
        i = (self.current_turn + 1) % len(self.player_handles)
        while i != self.current_turn:
            self.player_handles[i].notify_started_buy_phase(player_handle.name)
            i = (i + 1) % len(self.player_handles)
        player_handle.notify_started_buy_phase(player_handle.name)

    def finish_turn_for_player(self, player_handle):
        if not self.is_players_turn(player_handle) or self.current_phase != Phase.BUY:
            return

        self.cleanup_for(player_handle)

        self.current_turn = (self.current_turn + 1) % len(self.player_handles)
        self.current_phase = Phase.ACTION

        if self.current_turn == 0:
            self.turn_number += 1

    def cleanup_for(self, player_handle):
        state = self.player_state_by_handle[player_handle]

        self.gain_actions_for(player_handle, -state.actions + 1)
        self.gain_buys_for(player_handle, -state.buys + 1)
        self.gain_coins_for(player_handle, -state.coins)

        while len(state.hand) > 0:
            self.move_to_discard(player_handle, self.take_from_hand(player_handle, state.hand[0].name))

        while len(state.play_area) > 0:
            self.move_to_discard(player_handle, self.take_from_play_area(player_handle, state.play_area[0].name))

        for i in range(min(5, state.num_cards())):
            self.draw_card_for(player_handle)

    def play_card_for(self, player_handle, card_name):
        if not self.is_players_turn(player_handle) or not self.current_phase == Phase.ACTION:
            return

        card = self.take_from_hand(player_handle, card_name)
        self.play_card(player_handle, card)

        if card.is_action():
            self.gain_actions_for(player_handle, -1)

    def play_card(self, player_handle, card):
        state = self.player_state_by_handle[player_handle]

        for played_card in state.play_area:
            played_card.handle_card_played(player_handle, self, card.name)

        state.play_area.append(card)

        for handle in self.player_handles:
            handle.notify_played_card(player_handle.name, card.name)

        card.play(player_handle, self)

        for played_card in state.play_area[:-1]:
            card.handle_card_played(player_handle, self, played_card.name)

    def buy_card_for(self, player_handle, card_name):
        if not self.is_players_turn(player_handle) or not self.current_phase == Phase.BUY \
                or not self.can_buy(card_name, self.player_state_by_handle[player_handle].coins):
            return

        card = self.buy(card_name)
        self.move_to_discard(player_handle, card)
        self.gain_buys_for(player_handle, -1)
        self.gain_coins_for(player_handle, -card.cost)

    def buy(self, card_name):
        card = self.card_piles_by_name[card_name].pop()
        for handle in self.player_handles:
            handle.notify_card_bought(card_name)
        return card

    def cards_can_buy_with(self, coins):
        return list(filter(lambda card_name: self.can_buy(card_name, coins), self.card_piles_by_name))

    def can_buy(self, card_name, coins):
        return self.card_is_available(card_name) and self.card_piles_by_name[card_name][0].cost <= coins

    def card_is_available(self, card_name):
        return card_name in self.card_piles_by_name and len(self.card_piles_by_name[card_name]) > 0

    def num_empty_piles(self):
        return len(self.empty_piles())

    def empty_piles(self):
        return list(filter(lambda card_name: len(self.card_piles_by_name[card_name]) == 0, self.card_piles_by_name))

    def number_of_cards(self, player_handle):
        return self.player_state_by_handle[player_handle].num_cards()

    def hand_of(self, player_handle):
        return self.player_state_by_handle[player_handle].hand

    def discard_of(self, player_handle):
        return self.player_state_by_handle[player_handle].discard

    def deck_of(self, player_handle):
        return self.player_state_by_handle[player_handle].deck

    def gain_actions_for(self, player_handle, amount):
        self.player_state_by_handle[player_handle].actions += amount
        for handle in self.player_handles:
            handle.notify_gained_actions(player_handle.name, amount)

    def gain_buys_for(self, player_handle, amount):
        self.player_state_by_handle[player_handle].buys += amount
        for handle in self.player_handles:
            handle.notify_gained_buys(player_handle.name, amount)

    def gain_coins_for(self, player_handle, amount):
        self.player_state_by_handle[player_handle].coins += amount
        for handle in self.player_handles:
            handle.notify_gained_coins(player_handle.name, amount)

    def draw_card_for(self, player_handle):
        self.move_to_hand(player_handle, self.take_from_deck(player_handle))

    def move_to_hand(self, player_handle, card):
        self.player_state_by_handle[player_handle].hand.append(card)
        for handle in self.player_handles:
            handle.notify_gained_card_to_hand(player_handle.name, card.name if handle == player_handle else '?')

    def move_to_deck(self, player_handle, card):
        self.player_state_by_handle[player_handle].deck.append(card)
        for handle in self.player_handles:
            handle.notify_gained_card_to_deck(player_handle.name, card.name if handle == player_handle else '?')

    def move_to_discard(self, player_handle, card):
        self.player_state_by_handle[player_handle].discard.append(card)
        for handle in self.player_handles:
            handle.notify_gained_card_to_discard(player_handle.name, card.name)

    def move_to_trash(self, player_handle, card):
        self.trash.append(card)
        for handle in self.player_handles:
            handle.notify_trashed_card(player_handle.name, card.name)

    def take_from_deck(self, player_handle):
        state = self.player_state_by_handle[player_handle]

        if len(state.deck) == 0:
            while len(state.discard) > 0:
                card = self.take_from_discard(player_handle, state.discard[0].name)
                self.move_to_deck(player_handle, card)
            random.shuffle(state.deck)

        card = state.deck.pop()
        player_handle.notify_took_card_from_deck(card.name)
        return card

    def take_from_hand(self, player_handle, card_name):
        state = self.player_state_by_handle[player_handle]
        index = list(map(lambda card: card.name, state.hand)).index(card_name)
        for handle in self.player_handles:
            handle.notify_took_card_from_hand(player_handle.name, card_name if handle == player_handle else '?')
        return state.hand.pop(index)

    def take_from_play_area(self, player_handle, card_name):
        state = self.player_state_by_handle[player_handle]
        index = list(map(lambda card: card.name, state.play_area)).index(card_name)
        for handle in self.player_handles:
            handle.notify_took_card_from_play_area(card_name)
        return state.play_area.pop(index)

    def take_from_discard(self, player_handle, card_name):
        state = self.player_state_by_handle[player_handle]
        index = list(map(lambda card: card.name, state.discard)).index(card_name)
        for handle in self.player_handles:
            handle.notify_took_card_from_discard(player_handle.name, card_name)
        return state.discard.pop(index)

    def move_to_temp(self, player_handle, card):
        # TODO notify?
        self.player_state_by_handle[player_handle].temp_area.append(card)

    def discard_temp_area(self, player_handle):
        # TODO notify?
        state = self.player_state_by_handle[player_handle]
        while len(state.temp_area) > 0:
            self.move_to_discard(player_handle, state.temp_area.pop())
