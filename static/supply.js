class Supply {
    constructor() {
        this.cardIsAction = {};
        this.cardCosts = {};
        this.supplyPiles = {};

        this.cardBitmaps = {};
        this.cardText = {};
        this.cardTextOutline = {};
    }

    handleNotifyJoinedGame(message) {
        this.cardIsAction = message.card_is_action;
        this.cardCosts = message.card_costs;
        this.supplyPiles = message.supply_piles;

        this.initializeSupplyPiles();
    }

    handleNotifyCardBought(message) {
        this.supplyPiles[message.card] -= 1;
        this.cardText[message.card].text = this.supplyPiles[message.card];
        this.cardTextOutline[message.card].text = this.supplyPiles[message.card];
        if (this.supplyPiles[message.card] == 0) {
            stage.removeChild(this.cardBitmaps[card]);
            stage.removeChild(this.cardTextOutline[card]);
            stage.removeChild(this.cardText[card]);
        }
    }

    initializeCardAt(card, x, y) {
        this.cardBitmaps[card] = makeCardAt(card, x, y);
        this.cardText[card] = makeTextAt(x + 7.5, y + 5, this.supplyPiles[card], "white", 0);
        this.cardTextOutline[card] = makeTextAt(x + 7.5, y + 5.5, this.supplyPiles[card], "black", 3);
        stage.addChild(this.cardBitmaps[card]);
        stage.addChild(this.cardTextOutline[card]);
        stage.addChild(this.cardText[card]);
    }

    initializeSupplyPiles() {
        var x = cardPadding;
        var y = cardHeight + 2 * cardPadding;
        for (var card of ['copper', 'silver', 'gold']) {
            this.initializeCardAt(card, x, y);
            x += cardWidth + cardPadding;
        }

        x = cardPadding;
        y += cardHeight + cardPadding;
        for (var card of ['curse', 'estate', 'duchy', 'province']) {
            this.initializeCardAt(card, x, y);
            x += cardWidth + cardPadding;
        }

        var defaultCards = ['copper', 'silver', 'gold', 'curse', 'estate', 'duchy', 'province'];
        var sortedCards = Object.keys(this.cardCosts).sort((a, b) => this.cardCosts[a] - this.cardCosts[b]).filter(card => !defaultCards.includes(card));

        x = 5 * (cardWidth + cardPadding) + cardPadding;
        y = cardHeight + 2 * cardPadding;
        for (var i = 0; i < 5; i++) {
            var card = sortedCards[i];
            this.initializeCardAt(card, x, y);
            x += cardWidth + cardPadding;
        }

        x = 5 * (cardWidth + cardPadding) + cardPadding;
        y = 2 * (cardHeight + cardPadding) + cardPadding;
        for (var i = 5; i < 10; i++) {
            var card = sortedCards[i];
            this.initializeCardAt(card, x, y);
            x += cardWidth + cardPadding;
        }
    }

    addClickListenerToCard(card, onClickFn) {
        this.cardBitmaps[card].addEventListener('click', onClickFn);
        highlightCard(this.cardBitmaps[card]);
    }

    removeClickListeners() {
        for (let card of Object.keys(this.supplyPiles)) {
            this.cardBitmaps[card].removeAllEventListeners('click');
            unhighlightCard(this.cardBitmaps[card]);
        }
    }
}
