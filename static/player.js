class Player {
    constructor(name, y, canInteract) {
        this.name = name;

        this.canInteract = canInteract;

        this.hand = [];
        this.discard = [];

        this.actions = 0;
        this.buys = 0;
        this.coins = 0;

        this.isMyTurn = false;
        this.phase = 'ACTION';

        this.handContainer = new createjs.Container();
        this.handContainer.x = 4 * (cardWidth + cardPadding) + cardPadding;
        this.handContainer.y = y;
        stage.addChild(this.handContainer);

        this.deckBitmap = makeCardAt('card_back', 2 * (cardWidth + cardPadding) + cardPadding, this.handContainer.y);
        stage.addChild(this.deckBitmap);

        this.discardBitmap = makeCardAt('card_back', 3 * (cardWidth + cardPadding) + cardPadding, this.handContainer.y);

        if (canInteract) {
            this.finishButton = document.getElementById('finishButton');
            this.finishButton.style.position = 'absolute';
            this.finishButton.style.display = 'none';
            this.finishButton.style.left = cardPadding + 'px';
            this.finishButton.style.top = this.handContainer.y + 'px';
        }

        this.actionsText = makeTextAt(10, this.handContainer.y + 30, "Actions: 0");
        this.buysText = makeTextAt(10, this.handContainer.y + 55, "Buys: 0");
        this.coinsText = makeTextAt(10, this.handContainer.y + 80, "Coins: 0");
        stage.addChild(this.actionsText, this.buysText, this.coinsText);
    }

    handleGainedCardToHand(message) {
        if (message.player === this.name) {
            this.hand.push(message.card);
            this.handContainer.addChild(makeCardAt(message.card, this.hand.length * (cardWidth + cardPadding), 0));
        }
    }

    handleTookCardFromHand(message) {
        if (message.player === this.name) {
            var index = this.hand.indexOf(message.card);
            this.hand.splice(index, 1);
            this.handContainer.removeChildAt(index);
            for (var i = index; i < this.hand.length; i++) {
                this.handContainer.getChildAt(i).x -= cardWidth + cardPadding;
            }
        }
    }

    handleGainedCardToDiscard(message) {
        if (message.player === this.name) {
            this.discard.push(message.card);
            if (this.discard.length == 1) {
                stage.addChild(this.discardBitmap);
            }
            setImageForCard(this.discardBitmap, message.card);
        }
    }

    handleTookCardFromDiscard(message) {
        var index = this.discard.indexOf(message.card);
        this.discard.splice(index, 1);
        if (this.discard.length == 0) {
            stage.removeChild(this.discardBitmap);
        } else {
            setImageForCard(this.discardBitmap, this.discard[this.discard.length - 1]);
        }
    }

    handleGainedActions(message) {
        if (message.player === this.name) {
            this.actions += message.amount;
            this.actionsText.text = "Actions: " + this.actions;

            if (this.isMyTurn && this.phase === 'ACTION' && this.canInteract) {
                this.removeClickListenersFromHand();
                this.addListenersToCardsCanPlay();
            }
        }
    }

    handleGainedBuys(message) {
        if (message.player === this.name) {
            this.buys += message.amount;
            this.buysText.text = "Buys: " + this.buys;

            if (this.isMyTurn && this.phase === 'BUY' && this.canInteract) {
                supply.removeClickListeners();
                this.addListenersToCardsCanBuy();
            }
        }
    }

    handleGainedCoins(message) {
        if (message.player === this.name) {
            this.coins += message.amount;
            this.coinsText.text = "Coins: " + this.coins;

            if (this.isMyTurn && this.phase === 'BUY' && this.canInteract) {
                supply.removeClickListeners();
                this.addListenersToCardsCanBuy();
            }
        }
    }

    handleStartedActionPhase(message) {
        this.isMyTurn = message.player === this.name;
        this.phase = 'ACTION';
        if (this.isMyTurn && this.canInteract) {
            this.finishButton.style.display = 'inline';
            this.finishButton.onclick = () => this.finishActionPhase();
            this.finishButton.innerHTML = 'Finish Action Phase';

            this.addListenersToCardsCanPlay();
        }
    }

    addListenersToCardsCanPlay() {
        for (let card of this.cardsCanPlay()) {
            this.addClickListenerToHand(card, () => {
                this.playCard(card);
                this.removeClickListenersFromHand();
            });
        }
    }

    addClickListenerToHand(card, onClickFn) {
        for (var i = 0; i < this.hand.length; i++) {
            if (this.hand[i] === card) {
                var cardBitmap = this.handContainer.getChildAt(i);
                cardBitmap.addEventListener('click', onClickFn);
                highlightCard(cardBitmap);
            }
        }
    }

    removeClickListenersFromHand() {
        this.handContainer.children.forEach(cardBitmap => {
            cardBitmap.removeAllEventListeners('click');
            unhighlightCard(cardBitmap);
        });
    }

    cardsCanPlay() {
        if (this.actions === 0) {
            return [];
        }

        return Array.from(new Set(this.hand.filter(card => supply.cardIsAction[card])));
    }

    handleStartedBuyPhase(message) {
        if (message.player === this.name && this.canInteract) {
            this.phase = 'BUY';

            this.finishButton.style.display = 'inline';
            this.finishButton.onclick = () => this.finishTurn();
            this.finishButton.innerHTML = 'Finish Turn';

            this.addListenersToCardsCanBuy();
        }
    }

    addListenersToCardsCanBuy() {
        for (let card of this.cardsCanBuy()) {
            supply.addClickListenerToCard(card, () => {
                this.buyCard(card);
                supply.removeClickListeners();
            });
        }
    }

    cardsCanBuy() {
        if (this.buys === 0) {
            return [];
        }

        return Object.keys(supply.supplyPiles).filter(card => supply.cardCosts[card] <= this.coins);
    }

    buyCard(card) {
        websocket.send(JSON.stringify({ type: 'buy_card', card: card }));
    }

    playCard(card) {
        websocket.send(JSON.stringify({ type: 'play_card', card: card }));
    }

    finishActionPhase() {
        websocket.send(JSON.stringify({ type: 'finish_action_phase' }));
        this.finishButton.style.display = 'none';
        this.removeClickListenersFromHand();
    }

    finishTurn() {
        this.isMyTurn = false;
        websocket.send(JSON.stringify({ type: 'finish_turn' }));
        this.finishButton.style.display = 'none';
        supply.removeClickListeners();
    }

    handleAskYesOrNo(message) {
        var answer = confirm(message.prompt);
        websocket.send(JSON.stringify({ type: 'answer_yes_or_no', answer: answer }));
    }

    handleChooseFromCollection(message) {
        while (true) {
            var choice = prompt('Choose card from: ' + message.collection);
            if (message.collection.includes(choice)) {
                websocket.send(JSON.stringify({ type: 'chosen_card', card: choice }));
                break;
            }
        }
    }
}

