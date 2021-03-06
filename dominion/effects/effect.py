def as_names(card_collection):
    return list(map(lambda card: card.name, card_collection))


class Effect:
    def invoke(self, player_handle, game, arg):
        return arg

    # callback that is called when another card is played
    def handle_card_played(self, player_handle, game, other_card):
        pass

    # callback that is called when the card this effect is attached to is moved to the discard pile
    def handle_cleaned_up(self):
        pass

    def into(self, next_effect):
        return Into(self, next_effect)

    def and_(self, other_effect):
        return And(self, other_effect)

    def for_each(self, effect):
        return self.into(ForEach(effect))

    def times(self, effect):
        return self.into(Times(effect))

    def greater_than(self, effect):
        return GreaterThan(self, effect)

    def less_than(self, effect):
        return LessThan(self, effect)


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

    def handle_cleaned_up(self):
        for effect in self.effects:
            effect.handle_cleaned_up()


class MakeOpponents(Effect):
    def __init__(self, effect):
        self.effect = effect

    def invoke(self, player_handle, game, arg):
        results = []
        for opponent_handle in game.opponents_of(player_handle):
            affects_opponent = True
            while affects_opponent and len(game.reactions_of(opponent_handle)) > 0 \
                    and opponent_handle.ask_yes_or_no('React to attack?'):
                cards = game.reactions_of(opponent_handle)
                card_names = as_names(cards)
                chosen_card = opponent_handle.choose_card_from(card_names)

                cancels_attack = cards[card_names.index(chosen_card)].react(opponent_handle, game)
                if cancels_attack:
                    affects_opponent = False

            if affects_opponent:
                results.append(self.effect.invoke(opponent_handle, game, arg))
            else:
                results.append(None)
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
    def __init__(self, card_constructor, effect):
        self.card_name = card_constructor.__name__
        self.effect = effect
        self.activated = False

    def handle_card_played(self, player_handle, game, other_card):
        if not self.activated and other_card == self.card_name:
            self.effect.invoke(player_handle, game, None)
            self.activated = True

    def handle_cleaned_up(self):
        self.activated = False


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


class GreaterThan(Effect):
    def __init__(self, effect1, effect2):
        self.effect1 = effect1
        self.effect2 = effect2

    def invoke(self, player_handle, game, arg):
        return self.effect1.invoke(player_handle, game, arg) > self.effect2.invoke(player_handle, game, arg)


class LessThan(Effect):
    def __init__(self, effect1, effect2):
        self.effect1 = effect1
        self.effect2 = effect2

    def invoke(self, player_handle, game, arg):
        return self.effect1.invoke(player_handle, game, arg) < self.effect2.invoke(player_handle, game, arg)
