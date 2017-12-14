from .base import *


def cellar():
    return make_card(cellar.__name__, cost=2, type=CardType.ACTION,
                     effect=InOrder(GainActions(1),
                                    While(AskYesOrNo('Discard another card?'),
                                          ChooseFromHand())
                                    .for_each(MoveToDiscard()).into(Count()).into(DrawNCards())))


def chapel():
    return make_card(chapel.__name__, cost=2, type=CardType.ACTION,
                     effect=InOrder(GainActions(1),
                                    While(AskYesOrNo('Trash another card?'),
                                          ChooseFromHand())
                                    .for_each(MoveToTrash())))


def moat():
    return make_card(moat.__name__, cost=2, type=CardType.ACTION | CardType.REACTION, effect=Const(2).times(DrawCard()))


def harbinger():
    return make_card(harbinger.__name__, cost=3, type=CardType.ACTION,
                     effect=InOrder(DrawCard(), GainActions(1),
                                    If(AskYesOrNo('Take card from discard?'),
                                       ChooseFromDiscard().into(MoveToDeck()))))


def merchant():
    return make_card(merchant.__name__, cost=3, type=CardType.ACTION,
                     effect=InOrder(DrawCard(), GainActions(1), GainCoins(1).when_first_played(silver)))


def vassal():
    return make_card(vassal.__name__, cost=3, type=CardType.ACTION,
                     effect=InOrder(GainCoins(2), DrawCard().into(
                         IfElse(CardIsAction().and_(AskYesOrNo('Play action?')), PlayCard(), MoveToDiscard()))))


def village():
    return make_card(village.__name__, cost=3, type=CardType.ACTION, effect=InOrder(DrawCard(), GainActions(2)))


def workshop():
    return make_card(workshop.__name__, cost=3, type=CardType.ACTION, effect=BuyFromSupplyUpTo(4).into(MoveToDiscard()))


def bureaucrat():
    return make_card(bureaucrat.__name__, cost=4, type=CardType.ACTION | CardType.ATTACK,
                     effect=InOrder(PopFromSupply(silver).into(MoveToDeck()),
                                    MakeOpponents(ChooseVictoryFromHand().into(MoveToDeck()))))


def militia():
    return make_card(militia.__name__, cost=4, type=CardType.ACTION | CardType.ATTACK,
                     effect=InOrder(GainCoins(2),
                                    MakeOpponents(While(HandSizeGreaterThan(3),
                                                        ChooseFromHand().into(MoveToDiscard())))))


def moneylender():
    return make_card(moneylender.__name__, cost=4, type=CardType.ACTION,
                     effect=If(HasCard(copper), InOrder(TakeFromHand(copper).into(MoveToTrash()), GainCoins(3))))


def poacher():
    return make_card(poacher.__name__, cost=4, type=CardType.ACTION,
                     effect=InOrder(DrawCard(), GainActions(1), GainCoins(1),
                                    NumEmptyPiles().times(ChooseFromHand().into(MoveToDiscard()))))


def remodel():
    return make_card(remodel.__name__, cost=4, type=CardType.ACTION,
                     effect=ChooseFromHand().into(
                         InOrder(MoveToTrash(), BuyFromSupplyUpToMore(2).into(MoveToDiscard()))))


def smithy():
    return make_card(smithy.__name__, cost=4, type=CardType.ACTION, effect=Const(3).times(DrawCard()))


def throne_room():
    return make_card(throne_room.__name__, cost=4, type=CardType.ACTION,
                     effect=ChooseFromHand().into(InOrder(PlayCard(), PlayCard())))


def bandit():
    return make_card(bandit.__name__, type=CardType.ACTION | CardType.ATTACK, cost=5,
                     effect=InOrder(PopFromSupply(gold).into(MoveToDiscard()),
                                    MakeOpponents(
                                        Const(2).times(PopCardFromDeck()).into(MoveAnyHighTreasureToTrash()).for_each(
                                            MoveToDiscard()))))


def council_room():
    return make_card(council_room.__name__, cost=5, type=CardType.ACTION,
                     effect=InOrder(Const(4).times(DrawCard()), GainBuys(1), MakeOpponents(DrawCard())))


def festival():
    return make_card(festival.__name__, cost=5, type=CardType.ACTION,
                     effect=InOrder(GainActions(2), GainBuys(1), GainCoins(2)))


def laboratory():
    return make_card(laboratory.__name__, cost=5, type=CardType.ACTION,
                     effect=InOrder(Const(2).times(DrawCard()), GainActions(1)))


def library():
    return make_card(library.__name__, cost=5, type=CardType.ACTION,
                     effect=While(HandSizeLessThan(7),
                                  PopCardFromDeck().into(
                                      IfElse(
                                          CardIsAction().and_(AskYesOrNo('Skip action card?')),
                                          MoveToTempArea(),
                                          MoveToHand()))
                                  ).into(DiscardTempArea()))


def market():
    return make_card(market.__name__, cost=5, type=CardType.ACTION,
                     effect=InOrder(DrawCard(), GainActions(1), GainBuys(1), GainCoins(1)))


def mine():
    return make_card(mine.__name__, cost=5, type=CardType.ACTION,
                     effect=ChooseTreasureFromHand().into(
                         InOrder(MoveToTrash(), BuyFromSupplyUpToMore(3).into(MoveToDiscard()))))


def sentry():
    return make_card(sentry.__name__, cost=5, type=CardType.ACTION,
                     effect=InOrder(DrawCard(), GainActions(1),
                                    Const(2).times(PopCardFromDeck())
                                    .for_each(
                                        IfElse(AskYesOrNo('Trash card?'),
                                               MoveToTrash(),
                                               IfElse(
                                                   AskYesOrNo('Discard card?'),
                                                   MoveToDiscard(),
                                                   Effect())))
                                    .into(
                                        IfElse(AskYesOrNo('Swap order?'),
                                               Reverse(),
                                               Effect()))
                                    .into(FilterOutNone())
                                    .for_each(MoveToDeck())))


def witch():
    return make_card(witch.__name__, type=CardType.ACTION | CardType.ATTACK, cost=5,
                     effect=InOrder(Const(2).times(DrawCard()),
                                    MakeOpponents(PopFromSupply(curse).into(MoveToDiscard()))))


def artisan():
    return make_card(artisan.__name__, cost=6, type=CardType.ACTION,
                     effect=InOrder(BuyFromSupplyUpTo(5).into(MoveToDiscard()), ChooseFromHand().into(MoveToDeck())))


DOMINION_CARDS = [cellar, chapel, moat, harbinger, merchant, vassal, village, workshop, bureaucrat, militia,
                  moneylender, poacher, remodel, smithy, throne_room, bandit, council_room, festival, laboratory,
                  library, market, mine, sentry, witch, artisan]
