from .effect import Effect, as_names


class ChooseFrom(Effect):
    def __init__(self, effect, card_type=None):
        self.effect = effect
        self.card_type = card_type

    def invoke(self, player_handle, game, arg):
        collection = self.effect.invoke(player_handle, game, arg)
        if self.card_type is not None:
            collection = list(filter(lambda card: card.is_type(self.card_type), collection))
        names = as_names(collection)
        return player_handle.choose_card_from(names)


class ChooseFromToSellWithMore(Effect):
    def __init__(self, effect, additional_coins, card_type=None):
        self.effect = effect
        self.additional_coins = additional_coins
        self.card_type = card_type

    def invoke(self, player_handle, game, arg):
        collection = self.effect.invoke(player_handle, game, arg)
        if self.card_type is not None:
            collection = list(filter(lambda card: card.is_type(self.card_type), collection))
        collection = list(
            filter(lambda c: len(game.cards_can_buy_with(c.cost + self.additional_coins)) > 0, collection))
        names = as_names(collection)
        return player_handle.choose_card_from(names)
