from .effect import Effect, as_names


class ChooseAndTake(Effect):
    def invoke(self, player_handle, game, collection):
        names = as_names(collection)
        card_name = player_handle.choose_card_from(names)
        return collection.pop(names.index(card_name))


class ChooseAndTakeHighTreasure(Effect):
    def invoke(self, player_handle, game, collection):
        names = as_names(collection)
        high_treasure_names = as_names(filter(lambda card: card.is_high_treasure(), collection))
        card_name = player_handle.choose_card_from(high_treasure_names)
        return collection.pop(names.index(card_name))


class TakeFromHand(Effect):
    def invoke(self, player_handle, game, card_name):
        return game.take_from_hand(player_handle, card_name)


class TakeFromDiscard(Effect):
    def invoke(self, player_handle, game, card_name):
        return game.take_from_discard(player_handle, card_name)


class PopCardFromDeck(Effect):
    def invoke(self, player_handle, game, arg):
        return game.take_from_deck(player_handle)


class PopFromSupply(Effect):
    def __init__(self, card_constructor):
        self.card_name = card_constructor.__name__

    def invoke(self, player_handle, game, arg):
        return game.buy(self.card_name)


class PopFromPlayArea(Effect):
    def __init__(self, card_constructor):
        self.card_name = card_constructor.__name__

    def invoke(self, player_handle, game, arg):
        return game.take_from_play_area(player_handle, self.card_name)


class CardsInHand(Effect):
    def __init__(self, card_type=None):
        self.card_type = card_type

    def invoke(self, player_handle, game, arg):
        cards = game.hand_of(player_handle)
        if self.card_type is not None:
            cards = list(filter(lambda c: c.is_type(self.card_type), cards))
        return cards


class CardsInDiscard(Effect):
    def invoke(self, player_handle, game, arg):
        return game.discard_of(player_handle)


class CardsNotInPlay(Effect):
    def invoke(self, player_handle, game, arg):
        return game.discard_of(player_handle) + game.deck_of(player_handle)


class CardsInSupplyCostingUpTo(Effect):
    def __init__(self, coins):
        self.coins = coins

    def invoke(self, player_handle, game, arg):
        return game.cards_can_buy_with(self.coins)


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
