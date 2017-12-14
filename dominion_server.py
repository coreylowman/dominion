import json
import random
from flask import Flask
from flask_sockets import Sockets
from geventwebsocket.websocket import WebSocket

from dominion import Game, DOMINION_CARDS, PREMADE_GAMES, WebsocketPlayer, BigMoneyPlayer

app = Flask(__name__)
sockets = Sockets(app)


@sockets.route('/game')
def play_game(websocket: WebSocket):
    print('Websocket connnected')
    args = json.loads(websocket.receive())

    print('Starting game with {}'.format(args))

    if args['game'] == 'random':
        game = Game(random.sample(DOMINION_CARDS, 10))
    else:
        game = Game(PREMADE_GAMES[args['game']])

    game.add_player(BigMoneyPlayer('BigMoneyGuy'))
    game.add_player(WebsocketPlayer(args['name'], websocket))

    game.start()
    while not game.is_over():
        game.run_next_phase()
    game.complete()

    print('Finished game.')


@app.route('/')
def index():
    return app.send_static_file('index.html')


if __name__ == '__main__':
    from gevent import pywsgi
    from geventwebsocket.handler import WebSocketHandler

    server = pywsgi.WSGIServer(('localhost', 5000), app, handler_class=WebSocketHandler)
    server.serve_forever()
