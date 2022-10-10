import logging
import os
from os.path import join, dirname
from dotenv import load_dotenv
from flask import Flask
from flask_socketio import SocketIO

logging.basicConfig(format='%(asctime)s - %(message)s', datefmt='%d-%b-%y %H:%M:%S')

dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)

logging.debug('Starting app')

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY")

socketio = SocketIO(app, manage_session=False)

DATABASE = os.environ.get("DATABASE")

active_users = {}
game_count = 0