from flask import Flask

app = Flask(__name__)
app.secret_key = 'lM@0h@x0R'

DATABASE = 'blackjackDB'

active_players = []
active_users = {}
active_games = {}
