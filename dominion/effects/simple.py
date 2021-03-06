from .effect import Effect


class PlayCard(Effect):
    def invoke(self, player_handle, game, card):
        game.play_card(player_handle, card)


class GainActions(Effect):
    def __init__(self, amount):
        self.amount = amount

    def invoke(self, player_handle, game, arg):
        game.gain_actions_for(player_handle, self.amount)


class GainBuys(Effect):
    def __init__(self, amount):
        self.amount = amount

    def invoke(self, player_handle, game, arg):
        game.gain_buys_for(player_handle, self.amount)


class GainCoins(Effect):
    def __init__(self, amount):
        self.amount = amount

    def invoke(self, player_handle, game, arg):
        game.gain_coins_for(player_handle, self.amount)


class DrawCard(Effect):
    def invoke(self, player_handle, game, arg):
        game.draw_card_for(player_handle)


class Const(Effect):
    def __init__(self, value):
        self.value = value

    def invoke(self, player_handle, game, arg):
        return self.value


class NegateAttack(Const):
    def __init__(self):
        super().__init__(True)


class DontNegateAttack(Const):
    def __init__(self):
        super().__init__(False)
