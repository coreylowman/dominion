from .base import *


def baron():
    return make_card(baron.__name__, cost=4, type=CardType.ACTION,
                     effect=InOrder(GainBuys(1),
                                    IfElse(HasCard(estate).and_(AskYesOrNo('Discard estate?')),
                                           InOrder(Const('estate').into(TakeFromHand()).into(MoveToDiscard()),
                                                   GainCoins(4)),
                                           If(CardIsAvailable(estate), PopFromSupply(estate).into(MoveToDiscard())))
                                    ))


def bridge():
    # TODO
    pass


def courtyard():
    return make_card(courtyard.__name__, cost=2, type=CardType.ACTION,
                     effect=InOrder(Const(3).times(DrawCard()),
                                    ChooseFrom(CardsInHand()).into(TakeFromHand()).into(MoveToDeck())))


def duke():
    return make_victory(duke.__name__, cost=5, worth=NumberOf(duchy))


def harem():
    return make_card(harem.__name__, cost=6, type=CardType.TREASURE | CardType.VICTORY, effect=GainCoins(2),
                     worth=Const(2))


def mill():
    return make_card(mill.__name__, cost=4, type=CardType.ACTION | CardType.VICTORY,
                     effect=InOrder(DrawCard(), GainActions(1),
                                    If(Len(CardsInHand()).greater_than(Const(1)).and_(
                                        AskYesOrNo('Discard 2 cards for +2 coins?')),
                                        InOrder(Const(2).times(
                                            ChooseFrom(CardsInHand()).into(TakeFromHand()).into(MoveToDiscard())),
                                            GainCoins(2)))),
                     worth=Const(1))


def mining_village():
    return make_card(mining_village.__name__, cost=4, type=CardType.ACTION,
                     effect=InOrder(DrawCard(), GainActions(2),
                                    If(AskYesOrNo('Trash this for +2 coins?'),
                                       PopFromPlayArea(mining_village).into(MoveToTrash()))))


def nobles():
    return make_card(nobles.__name__, cost=6, type=CardType.Action | CardType.VICTORY,
                     effect=IfElse(AskYesOrNo('+3 cards? (otherwise +2 actions)'),
                                   Const(3).times(DrawCard),
                                   GainActions(2)),
                     worth=Const(2))
