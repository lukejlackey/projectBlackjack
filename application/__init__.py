from flask import Flask
from flask_socketio import SocketIO, join_room, leave_room, emit
from classes.active_games import active_games

app = Flask(__name__)
app.secret_key = 'lM@0h@x0R'

socketio = SocketIO(app, manage_session=False)

DATABASE = 'blackjackDB'

active_players = []
players_in_queue = []
ai_players = []
active_users = {}
game_count = 0
