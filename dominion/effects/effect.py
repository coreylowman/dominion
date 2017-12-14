def as_names(card_collection):
    return list(map(lambda card: card.name, card_collection))


class Effect:
    def invoke(self, player_handle, game, arg):
        return arg

    # callback that is called when another card is played
    def handle_card_played(self, player_handle, game, other_card):
        pass

    def into(self, next_effect):
        return Into(self, next_effect)

    def when_first_played(self, card_constructor):
        return WhenFirstPlayed(card_constructor.__name__, self)

    def and_(self, other_effect):
        return And(self, other_effect)

    def for_each(self, effect):
        return self.into(ForEach(effect))

    def times(self, effect):
        return self.into(Times(effect))


class If(Effect):
    def __init__(self, condition_effect, effect):
        self.condition_effect = condition_effect
        self.effect = effect

    def invoke(self, player_handle, game, arg):
        if self.condition_effect.invoke(player_handle, game, arg):
            return self.effect.invoke(player_handle, game, arg)


class IfElse(Effect):
    def __init__(self, condition_effect, true_effect, false_effect):
        self.condition_effect = condition_effect
        self.true_effect = true_effect
        self.false_effect = false_effect

    def invoke(self, player_handle, game, arg):
        if self.condition_effect.invoke(player_handle, game, arg):
            return self.true_effect.invoke(player_handle, game, arg)
        else:
            return self.false_effect.invoke(player_handle, game, arg)


class Into(Effect):
    def __init__(self, effect1, effect2):
        self.effect1 = effect1
        self.effect2 = effect2

    def invoke(self, player_handle, game, arg):
        arg = self.effect1.invoke(player_handle, game, arg)
        return self.effect2.invoke(player_handle, game, arg)


class InOrder(Effect):
    def __init__(self, *effects):
        self.effects = effects

    def invoke(self, player_handle, game, arg):
        results = []
        for effect in self.effects:
            results.append(effect.invoke(player_handle, game, arg))
        return results

    def handle_card_played(self, player_handle, game, other_card):
        for effect in self.effects:
            effect.handle_card_played(player_handle, game, other_card)


class MakeOpponents(Effect):
    def __init__(self, effect):
        self.effect = effect

    def invoke(self, player_handle, game, arg):
        results = []
        for opponent_handle in game.opponents_of(player_handle):
            if game.player_has_moat(opponent_handle):
                results.append(None)
            else:
                results.append(self.effect.invoke(opponent_handle, game, arg))
        return results


class And(Effect):
    def __init__(self, effect1, effect2):
        self.effect1 = effect1
        self.effect2 = effect2

    def invoke(self, player_handle, game, arg):
        return self.effect1.invoke(player_handle, game, arg) and self.effect2.invoke(player_handle, game, arg)


class While(Effect):
    def __init__(self, condition_effect, effect):
        self.condition_effect = condition_effect
        self.effect = effect

    def invoke(self, player_handle, game, arg):
        results = []
        while self.condition_effect.invoke(player_handle, game, arg):
            results.append(self.effect.invoke(player_handle, game, arg))
        return results


class WhenFirstPlayed(Effect):
    def __init__(self, card_name, effect):
        self.card_name = card_name
        self.effect = effect
        self.activated = False

    def handle_card_played(self, player_handle, game, other_card):
        if not self.activated and other_card == self.card_name:
            self.effect.invoke(player_handle, game, None)
            self.activated = True


class ForEach(Effect):
    def __init__(self, effect):
        self.effect = effect

    def invoke(self, player_handle, game, collection):
        results = []
        for item in collection:
            results.append(self.effect.invoke(player_handle, game, item))
        return results


class Times(Effect):
    def __init__(self, effect):
        self.effect = effect

    def invoke(self, player_handle, game, count):
        results = []
        for i in range(count):
            results.append(self.effect.invoke(player_handle, game, None))
        return results


class FilterOutNone(Effect):
    def invoke(self, player_handle, game, collection):
        return list(filter(lambda item: item is not None, collection))
