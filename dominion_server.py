import json
from flask import Flask
from flask_sockets import Sockets
from geventwebsocket.websocket import WebSocket

from dominion import make_premade_game, make_random_game, WebsocketPlayer
import dominion.cards
import dominion_ai

app = Flask(__name__)
sockets = Sockets(app)


@sockets.route('/game')
def play_game(websocket: WebSocket):
    print('Websocket connnected')
    args = json.loads(websocket.receive())

    print('Starting game with {}'.format(args))

    player = WebsocketPlayer(args['name'], websocket)
    ai = getattr(dominion_ai, args['ai'])(args['ai'])

    if args['game'] == 'random':
        reqs = set(map(lambda req: getattr(dominion.cards, req), args['requires']))
        reqs.update(ai.requires())
        game = make_random_game(player, ai, reqs)
    else:
        game = make_premade_game(player, ai, args['game'])

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
