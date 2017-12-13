from .effect import Effect


class HandSizeLessThan(Effect):
    def __init__(self, size):
        self.size = size

    def invoke(self, player_handle, game, arg):
        return len(game.hand_of(player_handle)) < self.size


class HandSizeGreaterThan(Effect):
    def __init__(self, size):
        self.size = size

    def invoke(self, player_handle, game, arg):
        return len(game.hand_of(player_handle)) > self.size


class CardIsAction(Effect):
    def invoke(self, player_handle, game, card):
        return card.is_action()


class HasCard(Effect):
    def __init__(self, card_constructor):
        self.name = card_constructor.__name__

    def invoke(self, player_handle, game, arg):
        return self.name in game.hand_of(player_handle, as_names=True)


class AskYesOrNo(Effect):
    def __init__(self, prompt):
        self.prompt = prompt

    def invoke(self, player_handle, game, arg):
        return player_handle.ask_yes_or_no(self.prompt)
