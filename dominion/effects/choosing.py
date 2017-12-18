from .effect import Effect, as_names


class ChooseFrom(Effect):
    def __init__(self, effect, card_type=None):
        self.effect = effect
        self.card_type = card_type

    def invoke(self, player_handle, game, arg):
        collection = self.effect.invoke(player_handle, game, arg)
        if self.card_type is not None:
            names = as_names(list(filter(lambda card: card.is_type(self.card_type), collection)))
        else:
            names = as_names(collection)
        return player_handle.choose_card_from(names)
