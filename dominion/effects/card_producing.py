from .effect import Effect, as_names


class TakeFromHand(Effect):
    def __init__(self, card_constructor):
        self.name = card_constructor.__name__

    def invoke(self, player_handle, game, arg):
        return game.take_from_hand(player_handle, self.name)


class PopCardFromDeck(Effect):
    def invoke(self, player_handle, game, arg):
        return game.take_from_deck(player_handle)


class PopFromSupply(Effect):
    def __init__(self, card_constructor):
        self.card_name = card_constructor.__name__

    def invoke(self, player_handle, game, arg):
        return game.buy(self.card_name)


class ChooseFromCollection(Effect):
    def invoke(self, player_handle, game, collection):
        names = as_names(collection)
        card_name = player_handle.choose_card_from(names)
        return collection.pop(names.index(card_name))


class ChooseHighTreasureFromCollection(Effect):
    def invoke(self, player_handle, game, collection):
        names = as_names(collection)
        high_treasure_names = as_names(filter(lambda card: card.is_high_treasure(), collection))

        card_name = player_handle.choose_card_from(high_treasure_names)
        return collection.pop(names.index(card_name))


class ChooseFrom(Effect):
    def __init__(self, effect, card_type=None):
        self.effect = effect
        self.card_type = card_type

    def invoke(self, player_handle, game, arg):
        collection = self.effect.invoke(player_handle, game, arg)
        names = as_names(collection)
        if self.card_type is not None:
            choices = as_names(list(filter(lambda card: card.is_type(self.card_type), collection)))
        else:
            choices = names
        card_name = player_handle.choose_card_from(choices)
        return collection.pop(names.index(card_name))


class CardsInHand(Effect):
    def invoke(self, player_handle, game, arg):
        return game.hand_of(player_handle)


class CardsInDiscard(Effect):
    def invoke(self, player_handle, game, arg):
        return game.discard_of(player_handle)


class CardsNotInPlay(Effect):
    def invoke(self, player_handle, game, arg):
        return game.discard_of(player_handle) + game.deck_of(player_handle)


class BuyFromSupplyUpTo(Effect):
    def __init__(self, coins):
        self.coins = coins

    def invoke(self, player_handle, game, arg):
        return game.buy(player_handle.choose_card_from(game.cards_can_buy_with(self.coins)))


class BuyFromSupplyUpToMore(Effect):
    def __init__(self, additional_coins):
        self.additional_coins = additional_coins

    def invoke(self, player_handle, game, card):
        cost = card.cost + self.additional_coins
        return game.buy(player_handle.choose_card_from(game.cards_can_buy_with(cost)))
