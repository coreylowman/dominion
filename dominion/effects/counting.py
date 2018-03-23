from . import Effect, as_names


class LogDeckSize(Effect):
    def invoke(self, player_handle, game, arg):
        return game.number_of_cards(player_handle) // 10


class NumEmptyPiles(Effect):
    def invoke(self, player_handle, game, arg):
        return game.num_empty_piles()


class Count(Effect):
    def invoke(self, player_handle, game, collection):
        return len(collection)


class Len(Effect):
    def __init__(self, collection_effect):
        self.effect = collection_effect

    def invoke(self, player_handle, game, arg):
        return len(self.effect.invoke(player_handle, game, arg))


class NumberOf(Effect):
    def __init__(self, card_constructor):
        self.card = card_constructor.__name__

    def invoke(self, player_handle, game, arg):
        return len(list(filter(lambda name: name == self.card, as_names(game.cards_of(player_handle)))))
