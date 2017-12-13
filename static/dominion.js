var name = 'corey';

var websocket;

var canvas = document.getElementById("dominionCanvas");
canvas.width = document.body.clientWidth;
canvas.height = document.body.clientHeight;

var stage = new createjs.Stage("dominionCanvas");

var cardWidth = 120;
var cardHeight = 192;
var cardPadding = 15;

var playArea;
var supply;
var player;
var opponent;

var messageHandlers = {
    notify_player_joined: [],
    notify_joined_game: [],
    notify_started_game: [],
    notify_started_action_phase: [],
    notify_started_buy_phase: [],
    notify_gained_actions: [],
    notify_gained_buys: [],
    notify_gained_coins: [],
    notify_gained_card_to_hand: [],
    notify_gained_card_to_deck: [],
    notify_gained_card_to_discard: [],
    notify_trashed_card: [],
    notify_took_card_from_hand: [],
    notify_took_card_from_play_area: [],
    notify_took_card_from_deck: [],
    notify_took_card_from_discard: [],
    notify_played_card: [],
    notify_card_bought: [],
    choose_card_from: [],
    ask_yes_or_no: [],
};

loadCards(main);

window.onresize = () => {
    canvas.width = document.body.clientWidth;
    canvas.height = document.body.clientHeight;
    stage.update();
};

function main() {
    playArea = new PlayArea();

    messageHandlers['notify_played_card'].push((message) => playArea.handleAddedCardToPlayArea(message));
    messageHandlers['notify_took_card_from_play_area'].push((message) => playArea.handleTookCardFromPlayArea(message));

    supply = new Supply();

    messageHandlers['notify_joined_game'].push((message) => supply.handleNotifyJoinedGame(message));
    messageHandlers['notify_card_bought'].push((message) => supply.handleNotifyCardBought(message));

    player = new Player(name, 3.5 * (cardHeight + 10), true);

    messageHandlers['notify_gained_card_to_hand'].push((message) => player.handleGainedCardToHand(message));
    messageHandlers['notify_gained_card_to_discard'].push((message) => player.handleGainedCardToDiscard(message));
    messageHandlers['notify_took_card_from_hand'].push((message) => player.handleTookCardFromHand(message));
    messageHandlers['notify_took_card_from_discard'].push((message) => player.handleTookCardFromDiscard(message));
    messageHandlers['notify_gained_actions'].push((message) => player.handleGainedActions(message));
    messageHandlers['notify_gained_buys'].push((message) => player.handleGainedBuys(message));
    messageHandlers['notify_gained_coins'].push((message) => player.handleGainedCoins(message));
    messageHandlers['notify_started_action_phase'].push((message) => player.handleStartedActionPhase(message));
    messageHandlers['notify_started_buy_phase'].push((message) => player.handleStartedBuyPhase(message));
    messageHandlers['ask_yes_or_no'].push((message) => player.handleAskYesOrNo(message));
    messageHandlers['choose_card_from'].push((message) => player.handleChooseFromCollection(message));

    messageHandlers['notify_player_joined'].push(handleOpponentJoined);

    websocket = new WebSocket("ws://localhost:5000/game");
    websocket.onopen = onConnect;
    websocket.onclose = onDisconnect;
    websocket.onmessage = onMessage;
    websocket.onerror = onError;
}

function onConnect(event) {
    console.log("connected!");

    var args = {
        name: name,
        game: 'First Game',
    };
    websocket.send(JSON.stringify(args));
}

function onDisconnect(event) {
    console.log("disconnected!");
}

function onMessage(event) {
    var message = JSON.parse(event.data);
    if (message.type in messageHandlers) {
        for (let handler of messageHandlers[message.type]) {
            handler(message);
        }
        stage.update();
    }
}

function onError(event) {
    console.log("error!");
    console.log(event);
}

function handleOpponentJoined(message) {
    opponent = new Player(message.player, 10, false);

    messageHandlers['notify_gained_card_to_hand'].push((message) => opponent.handleGainedCardToHand(message));
    messageHandlers['notify_gained_card_to_discard'].push((message) => opponent.handleGainedCardToDiscard(message));
    messageHandlers['notify_took_card_from_hand'].push((message) => opponent.handleTookCardFromHand(message));
    messageHandlers['notify_took_card_from_discard'].push((message) => opponent.handleTookCardFromDiscard(message));
    messageHandlers['notify_gained_actions'].push((message) => opponent.handleGainedActions(message));
    messageHandlers['notify_gained_buys'].push((message) => opponent.handleGainedBuys(message));
    messageHandlers['notify_gained_coins'].push((message) => opponent.handleGainedCoins(message));
}
