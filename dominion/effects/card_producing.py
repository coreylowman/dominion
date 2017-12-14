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


class ChooseFromHand(Effect):
    def invoke(self, player_handle, game, arg):
        card_name = player_handle.choose_card_from(as_names(game.hand_of(player_handle)))
        return game.take_from_hand(player_handle, card_name)


class ChooseVictoryFromHand(Effect):
    def invoke(self, player_handle, game, arg):
        victory_cards = list(filter(lambda card: card.is_victory(), game.hand_of(player_handle)))
        card_name = player_handle.choose_card_from(as_names(victory_cards))
        return game.take_from_hand(player_handle, card_name)


class ChooseTreasureFromHand(Effect):
    def invoke(self, player_handle, game, arg):
        treasure_cards = list(filter(lambda card: card.is_treasure(), game.hand_of(player_handle)))
        card_name = player_handle.choose_card_from(as_names(treasure_cards))
        return game.take_from_hand(player_handle, card_name)


class ChooseFromDiscard(Effect):
    def invoke(self, player_handle, game, arg):
        card_name = player_handle.choose_card_from(as_names(game.discard_of(player_handle)))
        return game.take_from_discard(player_handle, card_name)


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
