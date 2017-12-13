from . import Effect


class DiscardTempArea(Effect):
    def invoke(self, player_handle, game, arg):
        game.discard_temp_area(player_handle)
