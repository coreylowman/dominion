from .card import *
from .base import *
from .dominion import *

ALL_CARDS = BASE_CARDS + DOMINION_CARDS
ALL_CARD_NAMES = list(map(lambda cc: cc.__name__, ALL_CARDS))
