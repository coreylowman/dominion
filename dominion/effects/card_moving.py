from .effect import Effect


class MoveToTempArea(Effect):
    def invoke(self, player_handle, game, card):
        game.move_to_temp(player_handle, card)


class MoveToHand(Effect):
    def invoke(self, player_handle, game, card):
        game.move_to_hand(player_handle, card)


class MoveToDeck(Effect):
    def invoke(self, player_handle, game, card):
        game.move_to_deck(player_handle, card)


class MoveToDiscard(Effect):
    def invoke(self, player_handle, game, card):
        game.move_to_discard(player_handle, card)


class MoveToTrash(Effect):
    def invoke(self, player_handle, game, card):
        game.move_to_trash(player_handle, card)


class MoveAnyHighTreasureToTrash(Effect):
    def invoke(self, player_handle, game, cards):
        names = list(map(lambda card: card.name, cards))
        if 'silver' in names:
            game.move_to_trash(player_handle, cards.pop(names.index('silver')))
        elif 'gold' in names:
            game.move_to_trash(player_handle, cards.pop(names.index('gold')))
        return cards
