from .card import *


def estate():
    return make_victory(estate.__name__, cost=2, worth=Const(1))


def duchy():
    return make_victory(duchy.__name__, cost=5, worth=Const(3))


def province():
    return make_victory(province.__name__, cost=8, worth=Const(6))


def gardens():
    return make_victory(gardens.__name__, cost=4, worth=LogDeckSize())


def curse():
    return make_victory(curse.__name__, cost=0, type=CardType.CURSE, worth=Const(-1))


def copper():
    return make_card(copper.__name__, cost=0, type=CardType.TREASURE, effect=GainCoins(1))


def silver():
    return make_card(silver.__name__, cost=3, type=CardType.TREASURE, effect=GainCoins(2))


def gold():
    return make_card(gold.__name__, cost=6, type=CardType.TREASURE, effect=GainCoins(3))


BASE_CARDS = [estate, duchy, province, gardens, curse, copper, silver, gold]
