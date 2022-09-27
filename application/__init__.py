import logging
import os
from os.path import join, dirname
from dotenv import load_dotenv

from flask import Flask
from flask_socketio import SocketIO, join_room, leave_room, emit
from classes.active_games import active_games

logging.basicConfig(format='%(asctime)s - %(message)s', datefmt='%d-%b-%y %H:%M:%S')

dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY")

socketio = SocketIO(app, manage_session=False)

DATABASE = os.environ.get("DATABASE")

active_players = []
players_in_queue = []
ai_players = []
active_users = {}
game_count = 0
