from .effect import Effect


class DrawCard(Effect):
    def invoke(self, player_handle, game, arg):
        game.draw_card_for(player_handle)


class DrawNCards(Effect):
    def invoke(self, player_handle, game, number):
        for i in range(number):
            game.draw_card_for(player_handle)
