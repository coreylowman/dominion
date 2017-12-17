from . import Effect


class Const(Effect):
    def __init__(self, value):
        self.value = value

    def invoke(self, player_handle, game, arg):
        return self.value


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
