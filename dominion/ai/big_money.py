from dominion import AIPlayer
from dominion.cards import smithy

"""
Big Money AIs from http://wiki.dominionstrategy.com/index.php/Big_Money
"""


class BigMoneyPlayer(AIPlayer):
    def action_phase(self):
        pass

    def buy_phase(self):
        for card_name in ['province', 'gold', 'silver']:
            if self.can_buy(card_name):
                self.buy(card_name)

    def choose_card_from(self, collection):
        for card_name in ['province', 'duchy', 'estate', 'copper', 'silver', 'gold']:
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

    def buy_phase(self):
        if self.can_buy('smithy') and self.turn_number < 3:
            self.buy('smithy')
        else:
            super().buy_phase()


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

    def buy_phase(self):
        self.buy(self.get_card_to_buy())
