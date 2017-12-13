from unittest import TestCase
from dominion import *


class TestPlayer(PlayerHandle):
    def __init__(self):
        super().__init__('tester')

        self.answers = []
        self.choices = []

    def choose_card_from(self, collection):
        return self.choices.pop(0)

    def ask_yes_or_no(self, prompt):
        return self.answers.pop(0)


class CardTestCard(TestCase):
    def setUp(self):
        self.game = Game([])

        self.player_handle = TestPlayer()
        self.game.add_player(self.player_handle)
        self.player = self.game.player_state_by_handle[self.player_handle]
        self._empty(self.player)

        self.other_player_handle = TestPlayer()
        self.game.add_player(self.other_player_handle)
        self.other_player = self.game.player_state_by_handle[self.other_player_handle]
        self._empty(self.other_player)

    def _victory_points_of(self, card):
        return card.victory_points.invoke(self.player_handle, self.game, None)

    def _empty(self, player):
        player.actions = 0
        player.buys = 0
        player.coins = 0

        player.deck = []
        player.hand = []
        player.discard = []
        player.temp_area = []

    def _make(self, *cards):
        result = []
        for n, card_constructor in cards:
            for i in range(n):
                result.append(card_constructor())
        return result

    def _play(self, card):
        self.game.play_card(self.player_handle, card)

    def test_type(self):
        self.assertFalse(copper().is_action())
        self.assertFalse(copper().is_victory())
        self.assertTrue(copper().is_treasure())

        self.assertTrue(moat().is_action())

        self.assertTrue(estate().is_victory())

    def test_victory_cards(self):
        self.assertEqual(self._victory_points_of(curse()), -1)
        self.assertEqual(self._victory_points_of(estate()), 1)
        self.assertEqual(self._victory_points_of(duchy()), 3)
        self.assertEqual(self._victory_points_of(province()), 6)
        self.assertEqual(self._victory_points_of(gardens()), 0)

        for i in range(30):
            self.game.move_to_deck(self.player_handle, copper())
            self.assertEqual(self.game.number_of_cards(self.player_handle), i + 1)
            self.assertEqual(self._victory_points_of(gardens()), ((i + 1) // 10))

    def test_coins(self):
        self._play(copper())
        self.assertEqual(self.player.coins, 1)

        self._play(silver())
        self.assertEqual(self.player.coins, 3)

        self._play(gold())
        self.assertEqual(self.player.coins, 6)

    def test_cellar_all(self):
        """
        Discards all cards from the hand
        :return:
        """
        self.player.deck = self._make((4, copper))
        self.player.hand = self._make((4, curse))
        self.player_handle.answers = [True, True, True, True, False]  # discard the rest of the hand
        self.player_handle.choices = ['curse'] * 4
        self._play(cellar())

        self.assertEqual(len(self.player.deck), 0)
        self.assertListEqual(self.player.hand, self._make((4, copper)))
        self.assertListEqual(self.player.play_area, self._make((1, cellar)))
        self.assertListEqual(self.player.discard, self._make((4, curse)))

    def test_cellar_2(self):
        """
        Discards two cards from the hand
        :return:
        """
        self.player.deck = self._make((4, copper))
        self.player.hand = self._make((4, curse))
        self.player_handle.answers = [True, True, False]
        self.player_handle.choices = ['curse'] * 2
        self._play(cellar())

        self.assertListEqual(self.player.deck, self._make((2, copper)))
        self.assertListEqual(self.player.hand, self._make((2, curse), (2, copper)))
        self.assertListEqual(self.player.play_area, self._make((1, cellar)))
        self.assertListEqual(self.player.discard, self._make((2, curse)))

    def test_chapel_all(self):
        """
        Trashes all cards from the hand
        :return:
        """
        self.player.deck = self._make((4, copper))
        self.player.hand = self._make((4, curse))
        self.player_handle.answers = [True, True, True, True, False]
        self.player_handle.choices = ['curse'] * 4
        self._play(chapel())

        self.assertListEqual(self.player.deck, self._make((4, copper)))
        self.assertListEqual(self.player.hand, [])
        self.assertListEqual(self.player.play_area, self._make((1, chapel)))
        self.assertListEqual(self.player.discard, [])
        self.assertListEqual(self.game.trash, self._make((4, curse)))

    def test_chapel_2(self):
        """
        Trashes 2 cards from hand
        :return:
        """
        self.player.deck = self._make((4, copper))
        self.player.hand = self._make((4, curse))
        self.player_handle.answers = [True, True, False]
        self.player_handle.choices = ['curse'] * 2
        self._play(chapel())

        self.assertListEqual(self.player.deck, self._make((4, copper)))
        self.assertListEqual(self.player.hand, self._make((2, curse)))
        self.assertListEqual(self.player.play_area, self._make((1, chapel)))
        self.assertListEqual(self.player.discard, [])
        self.assertListEqual(self.game.trash, self._make((2, curse)))

    def test_moat(self):
        self.player.deck = self._make((4, copper))
        self._play(moat())

        self.assertListEqual(self.player.deck, self._make((2, copper)))
        self.assertListEqual(self.player.hand, self._make((2, copper)))

    def test_harbinger(self):
        self.player.discard = self._make((2, copper), (3, silver), (2, gold))
        self.player.deck = self._make((3, curse))

        # take a gold from discard
        self.player_handle.answers = [True]
        self.player_handle.choices = ['gold']
        self._play(harbinger())
        self.assertEqual(self.player.actions, 1)
        self.assertListEqual(self.player.hand, self._make((1, curse)))
        self.assertListEqual(self.player.discard, self._make((2, copper), (3, silver), (1, gold)))
        self.assertListEqual(self.player.deck, self._make((2, curse), (1, gold)))

        # don't take anything from discard
        self.player_handle.answers = [False]
        self._play(harbinger())
        self.assertEqual(self.player.actions, 2)
        self.assertListEqual(self.player.hand, self._make((1, curse), (1, gold)))
        self.assertListEqual(self.player.discard, self._make((2, copper), (3, silver), (1, gold)))
        self.assertListEqual(self.player.deck, self._make((2, curse)))

        # take silver from discard
        self.player_handle.answers = [True]
        self.player_handle.choices = ['silver']
        self._play(harbinger())
        self.assertEqual(self.player.actions, 3)
        self.assertListEqual(self.player.hand, self._make((1, curse), (1, gold), (1, curse)))
        self.assertListEqual(self.player.discard, self._make((2, copper), (2, silver), (1, gold)))
        self.assertListEqual(self.player.deck, self._make((1, curse), (1, silver)))

        # take copper from discard
        self.player_handle.answers = [True]
        self.player_handle.choices = ['copper']
        self._play(harbinger())
        self.assertEqual(self.player.actions, 4)
        self.assertListEqual(self.player.hand, self._make((1, curse), (1, gold), (1, curse), (1, silver)))
        self.assertListEqual(self.player.discard, self._make((1, copper), (2, silver), (1, gold)))
        self.assertListEqual(self.player.deck, self._make((1, curse), (1, copper)))

    def test_merchant(self):
        self.player.deck = self._make((2, curse))

        self._play(merchant())
        self.assertEqual(self.player.actions, 1)
        self.assertEqual(self.player.coins, 0)
        self.assertListEqual(self.player.deck, self._make((1, curse)))
        self.assertListEqual(self.player.hand, self._make((1, curse)))

        self._play(silver())
        self.assertEqual(self.player.coins, 3)

        self._play(merchant())
        self.assertEqual(self.player.actions, 2)
        self.assertEqual(self.player.coins, 4)
        self.assertListEqual(self.player.deck, [])
        self.assertListEqual(self.player.hand, self._make((2, curse)))

        self._play(silver())
        self.assertEqual(self.player.coins, 6)

    def test_vassal(self):
        pass

    def test_village(self):
        self.player.deck = self._make((1, curse))

        self._play(village())
        self.assertEqual(self.player.actions, 2)
        self.assertListEqual(self.player.deck, [])
        self.assertListEqual(self.player.hand, self._make((1, curse)))

    def test_workshop(self):
        pass

    def test_bureaucrat(self):
        pass

    def test_militia(self):
        pass

    def test_moneylender(self):
        pass

    def test_poacher(self):
        pass

    def test_remodel(self):
        pass

    def test_smithy(self):
        self.player.deck = self._make((4, curse))

        self._play(smithy())

        self.assertListEqual(self.player.deck, self._make((1, curse)))
        self.assertListEqual(self.player.hand, self._make((3, curse)))

    def test_throne_room(self):
        self.player.deck = self._make((8, curse))
        self.player.hand = self._make((1, smithy))

        self.player_handle.choices = ['smithy']
        self._play(throne_room())

        self.assertListEqual(self.player.deck, self._make((2, curse)))
        self.assertListEqual(self.player.hand, self._make((6, curse)))

    def test_bandit(self):
        pass

    def test_council_room(self):
        self.player.deck = self._make((5, curse))
        self.other_player.deck = self._make((2, curse))

        self._play(council_room())

        self.assertEqual(self.player.buys, 1)
        self.assertListEqual(self.player.hand, self._make((4, curse)))
        self.assertListEqual(self.player.deck, self._make((1, curse)))
        self.assertListEqual(self.other_player.hand, self._make((1, curse)))
        self.assertListEqual(self.other_player.deck, self._make((1, curse)))

    def test_festival(self):
        self._play(festival())
        self.assertEqual(self.player.actions, 2)
        self.assertEqual(self.player.buys, 1)
        self.assertEqual(self.player.coins, 2)

    def test_laboratory(self):
        self.player.deck = self._make((3, curse))

        self._play(laboratory())

        self.assertEqual(self.player.actions, 1)
        self.assertListEqual(self.player.deck, self._make((1, curse)))
        self.assertListEqual(self.player.hand, self._make((2, curse)))

    def test_library(self):
        pass

    def test_market(self):
        self.player.deck = self._make((2, curse))

        self._play(market())

        self.assertEqual(self.player.actions, 1)
        self.assertEqual(self.player.buys, 1)
        self.assertEqual(self.player.coins, 1)
        self.assertListEqual(self.player.deck, self._make((1, curse)))
        self.assertListEqual(self.player.hand, self._make((1, curse)))

    def test_mine(self):
        pass

    def test_sentry(self):
        pass

    def test_witch(self):
        self.player.deck = self._make((2, copper))

        self._play(witch())

        self.assertListEqual(self.player.deck, [])
        self.assertListEqual(self.player.hand, self._make((2, copper)))
        self.assertListEqual(self.other_player.discard, self._make((1, curse)))

    def test_artisan(self):
        pass
