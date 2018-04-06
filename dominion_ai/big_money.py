from dominion import AIPlayer
from dominion.cards import smithy, witch

"""
Big Money AIs from http://wiki.dominionstrategy.com/index.php/Big_Money
"""


class BigMoneyPlayer(AIPlayer):
    def action_phase(self):
        pass

    def get_card_to_buy(self):
        for card_name in ['province', 'gold', 'silver']:
            if self.can_buy(card_name):
                return card_name

    def buy_phase(self):
        card_to_buy = self.get_card_to_buy()
        if card_to_buy is not None and self.can_buy(card_to_buy):
            self.buy(card_to_buy)

    def choose_card_from(self, collection):
        for card_name in ['curse', 'province', 'duchy', 'estate', 'copper', 'silver', 'gold']:
            if card_name in collection:
                return card_name

    def ask_yes_or_no(self, prompt):
        return False


class SmithyBigMoneyPlayer(BigMoneyPlayer):
    def requires(self):
        return [smithy]

    def action_phase(self):
        if self.can_play('smithy'):
            self.play('smithy')

    def get_card_to_buy(self):
        if self.can_buy('smithy') and self.num_owned('smithy') < 2:
            self.buy('smithy')
        else:
            return super().get_card_to_buy()


class WitchBigMoneyPlayer(BigMoneyPlayer):
    def requires(self):
        return [witch]

    def action_phase(self):
        if self.can_play('witch'):
            self.play('witch')

    def get_card_to_buy(self):
        if self.can_buy('witch') and self.num_owned('witch') < 2:
            self.buy('witch')
        else:
            return super().get_card_to_buy()


class OptimalBigMoneyPlayer(BigMoneyPlayer):
    def get_card_to_buy(self):
        num_provinces = self.num_left_of['province']

        if self.coins >= 8:
            return 'province'
        elif self.coins >= 6:
            return 'duchy' if num_provinces <= 4 and self.can_buy('duchy') else 'gold'
        elif self.coins >= 5:
            return 'duchy' if num_provinces <= 5 and self.can_buy('duchy') else 'silver'
        elif self.coins >= 3:
            return 'estate' if num_provinces <= 2 and self.can_buy('estate') else 'silver'
        elif self.coins >= 2 and num_provinces <= 3:
            return 'estate' if self.can_buy('estate') else None
        else:
            return None
