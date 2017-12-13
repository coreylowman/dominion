var allCards = ["bureaucrat", "card_back", "cellar", "chapel",
    "copper", "council_room", "curse", "duchy", "estate", "festival",
    "gardens", "gold", "harbinger", "laboratory", "library", "market",
    "merchant", "militia", "mine", "moat", "moneylender", "poacher",
    "province", "remodel", "sentry", "silver", "smithy", "throne_room",
    "vassal", "village", "witch", "workshop", "artisan", "bandit"];

var imageForCard = {};

var loadedImage = {};

function loadCards(onCompleteFn) {
    var toLoad = new Set(allCards);
    for (let card of allCards) {
        imageForCard[card] = new Image();
        imageForCard[card].src = '/static/res/cards/' + card + '.jpg';
        imageForCard[card].onload = function() {
            toLoad.delete(card);
            if (toLoad.size == 0) {
                onCompleteFn();
            }
        }
    }

    imageForCard['?'] = imageForCard['card_back'];
}

function makeCardWithTextAt(name, x, y, text) {
    var obj = {};
    obj.card = makeCardAt(name, x, y);
    obj.box = makeBoxAt(x + 5, y + 5, 20, 20, "red");
    obj.text = makeTextAt(x + 7.5, y + 7.5, text);
    return obj;
}

function makeCardAt(name, x, y) {
    var bitmap = new createjs.Bitmap(imageForCard[name]);
    bitmap.x = x;
    bitmap.y = y;
    bitmap.scaleX = cardWidth / imageForCard[name].width;
    bitmap.scaleY = cardHeight / imageForCard[name].height;
    return bitmap;
}

function setImageForCard(bitmap, name) {
    bitmap.image = imageForCard[name];
    bitmap.scaleX = cardWidth / imageForCard[name].width;
    bitmap.scaleY = cardHeight / imageForCard[name].height;
}

function makeBoxAt(x, y, width, height, color) {
    var box = new createjs.Shape();
    box.graphics.beginFill(color).drawRoundRect(x, y, width, height, 5);
    return box;
}

function makeTextAt(x, y, str) {
    var text = new createjs.Text(str, "15px Arial", "#ffffff");
    text.x = x;
    text.y = y;
    return text;
}
