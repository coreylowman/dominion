from .base import *


def cellar():
    return make_card(cellar.__name__, cost=2, type=CardType.ACTION,
                     effect=InOrder(GainActions(1),
                                    While(Len(CardsInHand()).greater_than(Const(0))
                                          .and_(AskYesOrNo('Discard another card?')),
                                          ChooseFrom(CardsInHand()))
                                    .for_each(MoveToDiscard()).into(Count()).times(DrawCard())))


def chapel():
    return make_card(chapel.__name__, cost=2, type=CardType.ACTION,
                     effect=InOrder(While(Len(CardsInHand()).greater_than(Const(0))
                                          .and_(AskYesOrNo('Trash another card?')),
                                          ChooseFrom(CardsInHand()))
                                    .for_each(MoveToTrash())))


def moat():
    return make_card(moat.__name__, cost=2, type=CardType.ACTION | CardType.REACTION, effect=Const(2).times(DrawCard()))


def harbinger():
    return make_card(harbinger.__name__, cost=3, type=CardType.ACTION,
                     effect=InOrder(DrawCard(), GainActions(1),
                                    If(Len(CardsInDiscard()).greater_than(Const(0))
                                       .and_(AskYesOrNo('Take card from discard?')),
                                       ChooseFrom(CardsInDiscard()).into(MoveToDeck()))))


def merchant():
    return make_card(merchant.__name__, cost=3, type=CardType.ACTION,
                     effect=InOrder(DrawCard(), GainActions(1), GainCoins(1).when_first_played(silver)))


def vassal():
    return make_card(vassal.__name__, cost=3, type=CardType.ACTION,
                     effect=InOrder(GainCoins(2),
                                    If(Len(CardsNotInPlay()).greater_than(Const(0)),
                                       PopCardFromDeck().into(
                                           IfElse(CardIsAction().and_(AskYesOrNo('Play action?')),
                                                  PlayCard(),
                                                  MoveToDiscard())))))


def village():
    return make_card(village.__name__, cost=3, type=CardType.ACTION, effect=InOrder(DrawCard(), GainActions(2)))


def workshop():
    return make_card(workshop.__name__, cost=3, type=CardType.ACTION, effect=BuyFromSupplyUpTo(4).into(MoveToDiscard()))


def bureaucrat():
    return make_card(bureaucrat.__name__, cost=4, type=CardType.ACTION | CardType.ATTACK,
                     effect=InOrder(If(CardIsAvailable(silver),
                                       PopFromSupply(silver).into(MoveToDeck())),
                                    MakeOpponents(
                                        If(HasCardType(CardType.VICTORY),
                                           ChooseFrom(CardsInHand(), CardType.VICTORY).into(MoveToDeck())))))


def militia():
    return make_card(militia.__name__, cost=4, type=CardType.ACTION | CardType.ATTACK,
                     effect=InOrder(GainCoins(2),
                                    MakeOpponents(While(Len(CardsInHand()).greater_than(Const(3)),
                                                        ChooseFrom(CardsInHand()).into(MoveToDiscard())))))


def moneylender():
    return make_card(moneylender.__name__, cost=4, type=CardType.ACTION,
                     effect=If(HasCard(copper), InOrder(TakeFromHand(copper).into(MoveToTrash()), GainCoins(3))))


def poacher():
    return make_card(poacher.__name__, cost=4, type=CardType.ACTION,
                     effect=InOrder(DrawCard(), GainActions(1), GainCoins(1),
                                    NumEmptyPiles().times(
                                        If(Len(CardsInHand()).greater_than(Const(0)),
                                           ChooseFrom(CardsInHand()).into(MoveToDiscard())))))


def remodel():
    return make_card(remodel.__name__, cost=4, type=CardType.ACTION,
                     effect=If(Len(CardsInHand()).greater_than(Const(0)),
                               ChooseFrom(CardsInHand()).into(
                                   InOrder(MoveToTrash(), BuyFromSupplyUpToMore(2).into(MoveToDiscard())))))


def smithy():
    return make_card(smithy.__name__, cost=4, type=CardType.ACTION, effect=Const(3).times(DrawCard()))


def throne_room():
    return make_card(throne_room.__name__, cost=4, type=CardType.ACTION,
                     effect=If(Len(CardsInHand()).greater_than(Const(0)),
                               ChooseFrom(CardsInHand()).into(InOrder(PlayCard(), PlayCard()))))


def bandit():
    return make_card(bandit.__name__, type=CardType.ACTION | CardType.ATTACK, cost=5,
                     effect=InOrder(If(CardIsAvailable(gold),
                                       PopFromSupply(gold).into(MoveToDiscard())),
                                    MakeOpponents(
                                        Const(2)
                                            .times(If(Len(CardsNotInPlay()).greater_than(Const(0)), PopCardFromDeck()))
                                            .into(FilterOutNone())
                                            .into(InOrder(If(CollectionHasHighTreasure(),
                                                             ChooseHighTreasureFromCollection().into(MoveToTrash())),
                                                          ForEach(MoveToDiscard()))))))


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
                     effect=While(
                         Len(CardsInHand()).less_than(Const(7)).and_(Len(CardsNotInPlay()).greater_than(Const(0))),
                         PopCardFromDeck().into(
                             IfElse(CardIsAction().and_(AskYesOrNo('Skip action card?')),
                                    MoveToTempArea(),
                                    MoveToHand()))
                     ).into(DiscardTempArea()))


def market():
    return make_card(market.__name__, cost=5, type=CardType.ACTION,
                     effect=InOrder(DrawCard(), GainActions(1), GainBuys(1), GainCoins(1)))


def mine():
    return make_card(mine.__name__, cost=5, type=CardType.ACTION,
                     effect=If(HasCardType(CardType.TREASURE),
                               ChooseFrom(CardsInHand(), CardType.VICTORY).into(
                                   InOrder(MoveToTrash(), BuyFromSupplyUpToMore(3).into(MoveToHand())))))


def sentry():
    return make_card(sentry.__name__, cost=5, type=CardType.ACTION,
                     effect=InOrder(DrawCard(), GainActions(1),
                                    Const(2).times(
                                        If(Len(CardsNotInPlay()).greater_than(Const(0)), PopCardFromDeck()))
                                    .into(FilterOutNone())
                                    .for_each(
                                        IfElse(AskYesOrNo('Trash card?'),
                                               MoveToTrash(),
                                               IfElse(
                                                   AskYesOrNo('Discard card?'),
                                                   MoveToDiscard(),
                                                   Effect())))
                                    .into(FilterOutNone())
                                    .into(While(Count().greater_than(Const(0)),
                                                ChooseFromCollection().into(MoveToDeck())))))


def witch():
    return make_card(witch.__name__, type=CardType.ACTION | CardType.ATTACK, cost=5,
                     effect=InOrder(Const(2).times(DrawCard()),
                                    MakeOpponents(
                                        If(CardIsAvailable(curse),
                                           PopFromSupply(curse).into(MoveToDiscard())))))


def artisan():
    return make_card(artisan.__name__, cost=6, type=CardType.ACTION,
                     effect=InOrder(BuyFromSupplyUpTo(5).into(MoveToHand()),
                                    ChooseFrom(CardsInHand()).into(MoveToDeck())))


DOMINION_CARDS = [cellar, chapel, moat, harbinger, merchant, vassal, village, workshop, bureaucrat, militia,
                  moneylender, poacher, remodel, smithy, throne_room, bandit, council_room, festival, laboratory,
                  library, market, mine, sentry, witch, artisan]
