class PlayArea {
    constructor() {
        this.playArea = [];

        this.playAreaContainer = new createjs.Container();
        this.playAreaContainer.x = 11 * (cardWidth + cardPadding) + cardPadding;
        this.playAreaContainer.y = (cardHeight + cardPadding);
        stage.addChild(this.playAreaContainer);
    }

    handleAddedCardToPlayArea(message) {
        this.playArea.push(message.card);
        var location = PlayArea.locationForPlayAreaCard(this.playArea.length - 1);
        this.playAreaContainer.addChild(makeCardAt(message.card, location.x, location.y));
    }

    handleTookCardFromPlayArea(message) {
        var index = this.playArea.indexOf(message.card);
        this.playArea.splice(index, 1);
        this.playAreaContainer.removeChildAt(index);
        for (var i = index; i < this.playArea.length; i++) {
            var location = PlayArea.locationForPlayAreaCard(i);
            this.playAreaContainer.getChildAt(i).x = location.x;
            this.playAreaContainer.getChildAt(i).y = location.y;
        }
    }

    static locationForPlayAreaCard(i) {
        return {
            x: i * cardWidth / 2,
            y: i * cardHeight / 4,
        };
    }
}
