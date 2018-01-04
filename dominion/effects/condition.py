from .effect import Effect, as_names


class CollectionHasHighTreasure(Effect):
    def invoke(self, player_handle, game, collection):
        return any(map(lambda card: card.is_high_treasure(), collection))


class CardIsAction(Effect):
    def invoke(self, player_handle, game, card):
        return card.is_action()


class HasCard(Effect):
    def __init__(self, card_constructor):
        self.name = card_constructor.__name__

    def invoke(self, player_handle, game, arg):
        return self.name in as_names(game.hand_of(player_handle))


class HasCardType(Effect):
    def __init__(self, type):
        self.type = type

    def invoke(self, player_handle, game, arg):
        return any(map(lambda card: card.is_type(self.type), game.hand_of(player_handle)))


class CardIsAvailable(Effect):
    def __init__(self, card_constructor):
        self.name = card_constructor.__name__

    def invoke(self, player_handle, game, arg):
        return game.card_is_available(self.name)


class AskYesOrNo(Effect):
    def __init__(self, prompt):
        self.prompt = prompt

    def invoke(self, player_handle, game, arg):
        return player_handle.ask_yes_or_no(self.prompt)


class AnyIn(Effect):
    def __init__(self, collection_effect):
        self.effect = collection_effect

    def invoke(self, player_handle, game, arg):
        return len(self.effect.invoke(player_handle, game, arg)) > 0
