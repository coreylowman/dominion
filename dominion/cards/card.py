from enum import Flag, auto

from ..effects import *


class CardType(Flag):
    TREASURE = auto()
    CURSE = auto()
    VICTORY = auto()
    ACTION = auto()
    REACTION = auto()
    ATTACK = auto()


class Card:
    def __init__(self, name, type, cost, victory_points, effect, can_react_effect, reaction_effect):
        self.name = name
        self.cost = cost
        self.victory_points = victory_points
        self.effect = effect
        self.type = type
        self.can_react_effect = can_react_effect
        self.reaction_effect = reaction_effect

    def is_type(self, card_type):
        return bool(self.type & card_type)

    def is_action(self):
        return self.is_type(CardType.ACTION)

    def is_reaction(self):
        return self.is_type(CardType.REACTION)

    def is_victory(self):
        return self.is_type(CardType.VICTORY)

    def is_treasure(self):
        return self.is_type(CardType.TREASURE)

    def is_high_treasure(self):
        return self.name != 'copper' and self.is_treasure()

    def play(self, player_handle, game):
        self.effect.invoke(player_handle, game, None)

    def handle_card_played(self, player_handle, game, card_name):
        self.effect.handle_card_played(player_handle, game, card_name)

    def handle_cleaned_up(self):
        self.effect.handle_cleaned_up()

    def can_react(self, player_handle, game):
        return self.can_react_effect.invoke(player_handle, game, None)

    def react(self, player_handle, game):
        return self.reaction_effect.invoke(player_handle, game, None)

    def __eq__(self, other):
        return self.name == other.name

    def __str__(self):
        return self.name

    def __repr__(self):
        return self.name


def make_card(name, cost, type, effect, worth=Const(0), can_react=None, reaction=None):
    return Card(name=name, type=type, cost=cost, victory_points=worth, effect=effect, can_react_effect=can_react,
                reaction_effect=reaction)


def make_victory(name, cost, worth, type=CardType.VICTORY):
    return Card(name=name, type=type, cost=cost, victory_points=worth, effect=Effect(), can_react_effect=None,
                reaction_effect=None)
