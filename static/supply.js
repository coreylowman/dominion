class Supply {
    constructor() {
        this.cardIsAction = {};
        this.cardCosts = {};
        this.supplyPiles = {};

        this.supplyObjects = {};
    }

    handleNotifyJoinedGame(message) {
        this.cardIsAction = message.card_is_action;
        this.cardCosts = message.card_costs;
        this.supplyPiles = message.supply_piles;

        this.initializeSupplyPiles();
    }

    handleNotifyCardBought(message) {
        this.supplyPiles[message.card] -= 1;
        this.supplyObjects[message.card].text.text = this.supplyPiles[message.card];
    }

    initializeSupplyPiles() {
        var x = 10;
        var y = cardHeight + 10 + 10;
        for (var card of ['copper', 'silver', 'gold']) {
            this.supplyObjects[card] = makeCardWithTextAt(card, x, y, this.supplyPiles[card]);
            x += cardWidth + 10;
        }

        x = 10;
        y += cardHeight + 10;
        for (var card of ['curse', 'estate', 'duchy', 'province']) {
            this.supplyObjects[card] = makeCardWithTextAt(card, x, y, this.supplyPiles[card]);
            x += cardWidth + 10;
        }

        var defaultCards = ['copper', 'silver', 'gold', 'curse', 'estate', 'duchy', 'province'];
        var sortedCards = Object.keys(this.cardCosts).sort((a, b) => this.cardCosts[a] - this.cardCosts[b]).filter(card => !defaultCards.includes(card));

        x = 5 * (cardWidth + 10) + 10;
        y = cardHeight + 10 + 10;
        for (var i = 0; i < 5; i++) {
            var card = sortedCards[i];
            this.supplyObjects[card] = makeCardWithTextAt(card, x, y, this.supplyPiles[card]);
            x += cardWidth + 10;
        }

        x = 5 * (cardWidth + 10) + 10;
        y = 2 * (cardHeight + 10) + 10;
        for (var i = 5; i < 10; i++) {
            var card = sortedCards[i];
            this.supplyObjects[card] = makeCardWithTextAt(card, x, y, this.supplyPiles[card]);
            x += cardWidth + 10;
        }

        for (var supplyObj of Object.values(this.supplyObjects)) {
            stage.addChild(supplyObj.card);
            stage.addChild(supplyObj.box);
            stage.addChild(supplyObj.text);
        }
    }

    addClickListenerToCard(card, onClickFn) {
        this.supplyObjects[card].card.addEventListener('click', onClickFn);
    }

    removeClickListeners() {
        for (let card of Object.keys(this.supplyPiles)) {
            this.supplyObjects[card].card.removeAllEventListeners('click');
        }
    }
}
