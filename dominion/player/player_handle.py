from abc import abstractmethod


class PlayerHandle:
    def __init__(self, name):
        self.name = name
        self.game = None

    def play(self, card_name):
        self.game.play_card_for(self, card_name)

    def buy(self, card_name):
        self.game.buy_card_for(self, card_name)

    def finish_action_phase(self):
        self.game.finish_action_phase_for_player(self)

    def finish_turn(self):
        self.game.finish_turn_for_player(self)

    def join_game(self, game):
        self.game = game

        supply_piles = {}
        card_costs = {}
        card_is_action = {}
        for card_name, cards in self.game.card_piles_by_name.items():
            supply_piles[card_name] = len(cards)
            card_costs[card_name] = cards[0].cost
            card_is_action[card_name] = cards[0].is_action()

        self.notify_joined_game(supply_piles, card_costs, card_is_action)

    @abstractmethod
    def notify_player_joined(self, player):
        pass

    @abstractmethod
    def notify_joined_game(self, supply_piles, card_costs, card_is_action):
        pass

    @abstractmethod
    def notify_started_game(self):
        pass

    @abstractmethod
    def notify_started_action_phase(self, player):
        pass

    @abstractmethod
    def notify_started_buy_phase(self, player):
        pass

    @abstractmethod
    def notify_gained_actions(self, player, amount):
        pass

    @abstractmethod
    def notify_gained_buys(self, player, amount):
        pass

    @abstractmethod
    def notify_gained_coins(self, player, amount):
        pass

    @abstractmethod
    def notify_gained_card_to_hand(self, player, card):
        pass

    @abstractmethod
    def notify_gained_card_to_deck(self, player, card):
        pass

    @abstractmethod
    def notify_gained_card_to_discard(self, player, card):
        pass

    @abstractmethod
    def notify_trashed_card(self, player, card):
        pass

    @abstractmethod
    def notify_took_card_from_hand(self, player, card):
        pass

    @abstractmethod
    def notify_took_card_from_play_area(self, card):
        pass

    @abstractmethod
    def notify_took_card_from_deck(self, card):
        pass

    @abstractmethod
    def notify_took_card_from_discard(self, player, card):
        pass

    @abstractmethod
    def notify_played_card(self, player, card):
        pass

    @abstractmethod
    def notify_card_bought(self, card):
        pass

    @abstractmethod
    def choose_card_from(self, collection):
        pass

    @abstractmethod
    def ask_yes_or_no(self, prompt):
        pass
