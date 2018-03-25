from dominion import AIPlayer
from dominion.cards import *


class RemodelBanditPlayer(AIPlayer):
    def requires(self):
        return [remodel, bandit, chapel]

    def action_phase(self):
        cards_to_trash = list(filter(lambda card: card == 'copper' or card == 'estate' or card == 'curse', self.hand))
        if self.num_of['gold'] >= self.num_left_of['province'] / 1.5 and 'gold' in self.hand and self.can_play(
                'remodel'):
            self._remodel('gold', 'province')
        elif self.can_play('chapel') and len(cards_to_trash) > 2:
            self._chapel(cards_to_trash)
        elif self.can_play('bandit'):
            self.play('bandit')
        elif self.can_play('chapel') and len(cards_to_trash) > 1:
            self._chapel(cards_to_trash)
        elif self.can_play('remodel'):
            if 'witch' not in self.num_left_of and \
                    'chapel' in self.hand and self.num_of['estate'] == 0 and self.num_of['copper'] == 0:
                self._remodel('chapel', 'silver')
            else:
                for a, b in [('estate', 'silver'), ('silver', 'duchy'), ('silver', 'bandit')]:
                    if a in self.hand and self.num_left_of[b] > 0:
                        self._remodel(a, b)
                        break
        elif self.can_play('chapel') and len(cards_to_trash) > 0:
            self._chapel(cards_to_trash)

    def _remodel(self, a, b):
        self.choices = [a, b]
        self.play('remodel')

    def _chapel(self, cards_to_trash):
        self.choices = cards_to_trash
        self.answers = [True] * len(self.choices)
        self.answers.append(False)
        self.play('chapel')

    def buy_phase(self):
        if self.turn_number <= 2:
            if self.can_buy('bandit'):
                self.buy('bandit')
            elif self.can_buy('chapel') and self.num_of['chapel'] == 0:
                self.buy('chapel')
            elif self.can_buy('silver'):
                self.buy('silver')
        elif self.can_buy('bandit') and self.num_of['bandit'] < 1:
            self.buy('bandit')
        elif self.can_buy('remodel') and self.num_of['remodel'] < 1:
            self.buy('remodel')
        elif self.can_buy('province'):
            self.buy('province')
        elif self.can_buy('gold'):
            self.buy('gold')
        elif self.can_buy('silver'):
            self.buy('silver')

    def choose_card_from(self, collection):
        if len(self.choices) > 0:
            return self.choices.pop(0)
        else:
            for card_name in ['province', 'duchy', 'estate', 'copper', 'silver', 'gold']:
                if card_name in collection:
                    return card_name

    def ask_yes_or_no(self, prompt):
        if len(self.answers) > 0:
            return self.answers.pop(0)
        else:
            return False


class VassalVillagePlayer(AIPlayer):
    def requires(self):
        return [vassal, village]

    def action_phase(self):
        while self.can_play_anything():
            if self.can_play('village'):
                self.play('village')
            elif self.can_play('vassal'):
                self.play('vassal')

    def buy_phase(self):
        if self.can_buy('province'):
            self.buy('province')
        elif self.can_buy('gold'):
            self.buy('gold')
        else:
            village_priority = self.num_of['village'] < self.num_of['vassal']
            if village_priority and self.can_buy('village'):
                self.buy('village')
            elif self.can_buy('vassal'):
                self.buy('vassal')
            elif self.can_buy('village'):
                self.buy('village')

    def choose_card_from(self, collection):
        for card_name in ['province', 'duchy', 'estate', 'copper', 'silver', 'gold']:
            if card_name in collection:
                return card_name

    def ask_yes_or_no(self, prompt):
        return True


class WorkshopGardensPlayer(AIPlayer):
    def requires(self):
        return [gardens, workshop]

    def action_phase(self):
        if self.can_play('workshop'):
            for card in sorted(['workshop', 'gardens', 'estate'], key=lambda card: self.num_of[card]):
                if self.num_left_of[card] > 0:
                    self._workshop(card)
                    break

    def _workshop(self, card_name):
        self.choices = [card_name]
        self.play('workshop')

    def buy_phase(self):
        for card in ['workshop', 'gardens', 'estate', 'copper']:
            if self.can_buy(card):
                self.buy(card)

    def choose_card_from(self, collection):
        if len(self.choices) > 0:
            return self.choices.pop(0)
        else:
            for card_name in ['province', 'duchy', 'estate', 'copper', 'silver', 'gold']:
                if card_name in collection:
                    return card_name

    def ask_yes_or_no(self, prompt):
        return False
