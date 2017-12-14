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
        self.game = Game(DOMINION_CARDS)

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
        self.player.deck = self._make((1, festival), (1, village), (1, curse))

        self._play(vassal())
        self.assertListEqual(self.player.discard, self._make((1, curse)))
        self.assertListEqual(self.player.deck, self._make((1, festival), (1, village)))

        self.player_handle.answers = [False]
        self._play(vassal())
        self.assertListEqual(self.player.discard, self._make((1, curse), (1, village)))
        self.assertListEqual(self.player.deck, self._make((1, festival)))
        self.assertListEqual(self.player.hand, [])
        self.assertEqual(self.player.actions, 0)

        self.player_handle.answers = [True]
        self._play(vassal())
        self.assertListEqual(self.player.discard, self._make((1, curse), (1, village)))
        self.assertListEqual(self.player.deck, [])
        self.assertListEqual(self.player.hand, [])
        self.assertEqual(self.player.actions, 2)
        self.assertEqual(self.player.buys, 1)
        self.assertEqual(self.player.coins, 8)

    def test_village(self):
        self.player.deck = self._make((1, curse))

        self._play(village())
        self.assertEqual(self.player.actions, 2)
        self.assertListEqual(self.player.deck, [])
        self.assertListEqual(self.player.hand, self._make((1, curse)))

    def test_workshop(self):
        self.player_handle.choices = ['smithy']
        self._play(workshop())

        self.assertListEqual(self.player.discard, self._make((1, smithy)))

    def test_bureaucrat_no_victory(self):
        self.other_player.hand = self._make((1, silver))

        self._play(bureaucrat())
        self.assertListEqual(self.player.deck, self._make((1, silver)))

    def test_bureaucrat(self):
        self.other_player.hand = self._make((1, copper), (1, province), (1, estate))
        self.other_player_handle.choices = ['province']

        self._play(bureaucrat())
        self.assertListEqual(self.player.deck, self._make((1, silver)))
        self.assertListEqual(self.other_player.hand, self._make((1, copper), (1, estate)))
        self.assertListEqual(self.other_player.deck, self._make((1, province)))

    def test_militia(self):
        self.other_player.hand = self._make((1, copper), (1, silver), (1, gold), (1, curse), (1, province))
        self.other_player_handle.choices = ['silver', 'curse']

        self._play(militia())

        self.assertListEqual(self.other_player.hand, self._make((1, copper), (1, gold), (1, province)))
        self.assertListEqual(self.other_player.discard, self._make((1, silver), (1, curse)))
        self.assertEqual(self.player.coins, 2)

    def test_moneylender(self):
        # no copper in hand
        self._play(moneylender())
        self.assertListEqual(self.game.trash, [])
        self.assertEqual(self.player.coins, 0)

        self.player.hand = self._make((1, curse))
        self._play(moneylender())
        self.assertListEqual(self.game.trash, [])
        self.assertEqual(self.player.coins, 0)

        self.player.hand = self._make((1, silver))
        self._play(moneylender())
        self.assertListEqual(self.game.trash, [])
        self.assertEqual(self.player.coins, 0)

        self.player.hand = self._make((1, copper))
        self._play(moneylender())
        self.assertListEqual(self.game.trash, self._make((1, copper)))
        self.assertEqual(self.player.coins, 3)

    def test_poacher(self):
        self.player.deck = self._make((4, curse))

        # no empty piles
        self._play(poacher())
        self.assertListEqual(self.player.deck, self._make((3, curse)))
        self.assertListEqual(self.player.hand, self._make((1, curse)))
        self.assertEqual(self.player.actions, 1)
        self.assertEqual(self.player.coins, 1)

        # copper pile empty - 1 discard
        self.game.card_piles_by_name['copper'] = []
        self.player_handle.choices = ['curse']

        self._play(poacher())
        self.assertListEqual(self.player.deck, self._make((2, curse)))
        self.assertListEqual(self.player.hand, self._make((1, curse)))
        self.assertListEqual(self.player.discard, self._make((1, curse)))
        self.assertEqual(self.player.actions, 2)
        self.assertEqual(self.player.coins, 2)

        # copper & silver pile empty - 2 discards
        self.game.card_piles_by_name['silver'] = []
        self.player.hand = self._make((1, estate), (1, duchy))
        self.player_handle.choices = ['estate', 'duchy']

        self._play(poacher())
        self.assertListEqual(self.player.deck, self._make((1, curse)))
        self.assertListEqual(self.player.hand, self._make((1, curse)))
        self.assertListEqual(self.player.discard, self._make((1, curse), (1, estate), (1, duchy)))
        self.assertEqual(self.player.actions, 3)
        self.assertEqual(self.player.coins, 3)

    def test_remodel(self):
        # empty hand - should have no effect
        self._play(remodel())

        self.player.hand = self._make((1, gold))
        self.player_handle.choices = ['gold', 'province']
        self._play(remodel())
        self.assertListEqual(self.game.trash, self._make((1, gold)))
        self.assertListEqual(self.player.hand, [])
        self.assertListEqual(self.player.discard, self._make((1, province)))

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

    def test_bandit_none(self):
        self.other_player.deck = self._make((1, curse), (1, copper))
        self._play(bandit())
        self.assertListEqual(self.other_player.deck, [])
        self.assertListEqual(self.other_player.discard, self._make((1, copper), (1, curse)))
        self.assertListEqual(self.game.trash, [])
        self.assertEqual(self.player.discard, self._make((1, gold)))

    def test_bandit_high_treasure(self):
        self.other_player_handle.choices = ['gold']
        self.other_player.deck = self._make((1, gold), (1, silver))
        self._play(bandit())
        self.assertListEqual(self.other_player.deck, [])
        self.assertListEqual(self.other_player.discard, self._make((1, silver)))
        self.assertListEqual(self.game.trash, self._make((1, gold)))
        self.assertEqual(self.player.discard, self._make((1, gold)))

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
        self.player.deck = self._make((1, silver), (1, festival), (5, copper), (1, smithy), (1, market))
        self.player_handle.answers = [True, True, False]

        self._play(library())
        self.assertListEqual(self.player.hand, self._make((5, copper), (1, festival), (1, silver)))
        self.assertListEqual(self.player.discard, self._make((1, smithy), (1, market)))

    def test_market(self):
        self.player.deck = self._make((2, curse))

        self._play(market())

        self.assertEqual(self.player.actions, 1)
        self.assertEqual(self.player.buys, 1)
        self.assertEqual(self.player.coins, 1)
        self.assertListEqual(self.player.deck, self._make((1, curse)))
        self.assertListEqual(self.player.hand, self._make((1, curse)))

    def test_mine(self):
        # no treasures in hand
        self._play(mine())
        self.assertListEqual(self.player.hand, [])

        self.player.hand = self._make((1, copper), (1, silver))

        # trash a copper to gain a village
        self.player_handle.choices = ['copper', 'village']
        self._play(mine())

        self.assertListEqual(self.player.hand, self._make((1, silver), (1, village)))
        self.assertListEqual(self.game.trash, self._make((1, copper)))

    def test_sentry_trash_trash(self):
        self.player.deck = self._make((1, smithy), (1, copper), (1, curse), (1, mine))

        # trash curse ([True]), trash copper ([True])
        self.player_handle.answers = [True, True]
        self._play(sentry())

        self.assertListEqual(self.player.deck, self._make((1, smithy)))
        self.assertListEqual(self.game.trash, self._make((1, curse), (1, copper)))
        self.assertListEqual(self.player.discard, [])
        self.assertListEqual(self.player.hand, self._make((1, mine)))
        self.assertEqual(self.player.actions, 1)

    def test_sentry_trash_discard(self):
        self.player.deck = self._make((1, smithy), (1, copper), (1, curse), (1, mine))

        # trash curse ([True]), discard copper ([False, True])
        self.player_handle.answers = [True, False, True]
        self._play(sentry())

        self.assertListEqual(self.player.deck, self._make((1, smithy)))
        self.assertListEqual(self.game.trash, self._make((1, curse)))
        self.assertListEqual(self.player.discard, self._make((1, copper)))
        self.assertListEqual(self.player.hand, self._make((1, mine)))
        self.assertEqual(self.player.actions, 1)

    def test_sentry_keep_all_reverse(self):
        self.player.deck = self._make((1, smithy), (1, copper), (1, curse), (1, mine))

        # keep curse ([False, False]), keep copper ([False, False])
        self.player_handle.answers = [False, False, False, False]
        # put curse on deck, then copper
        self.player_handle.choices = ['curse', 'copper']
        self._play(sentry())

        self.assertListEqual(self.player.deck, self._make((1, smithy), (1, curse), (1, copper)))
        self.assertListEqual(self.game.trash, [])
        self.assertListEqual(self.player.discard, [])
        self.assertListEqual(self.player.hand, self._make((1, mine)))
        self.assertEqual(self.player.actions, 1)

    def test_sentry_keep_all(self):
        self.player.deck = self._make((1, smithy), (1, copper), (1, curse), (1, mine))

        # keep curse ([False, False]), keep copper ([False, False])
        self.player_handle.answers = [False, False, False, False]
        # put curse on deck, then copper
        self.player_handle.choices = ['copper', 'curse']
        self._play(sentry())

        self.assertListEqual(self.player.deck, self._make((1, smithy), (1, copper), (1, curse)))
        self.assertListEqual(self.game.trash, [])
        self.assertListEqual(self.player.discard, [])
        self.assertListEqual(self.player.hand, self._make((1, mine)))
        self.assertEqual(self.player.actions, 1)

    def test_witch(self):
        self.player.deck = self._make((2, copper))

        self._play(witch())

        self.assertListEqual(self.player.deck, [])
        self.assertListEqual(self.player.hand, self._make((2, copper)))
        self.assertListEqual(self.other_player.discard, self._make((1, curse)))

    def test_artisan(self):
        self.player_handle.choices = ['market', 'market']
        self._play(artisan())

        self.assertListEqual(self.player.deck, self._make((1, market)))
        self.assertListEqual(self.player.hand, [])
        self.assertListEqual(self.player.discard, [])

        self.player.hand = self._make((1, curse))
        self.player_handle.choices = ['smithy', 'curse']
        self._play(artisan())

        self.assertListEqual(self.player.deck, self._make((1, market), (1, curse)))
        self.assertListEqual(self.player.hand, self._make((1, smithy)))
