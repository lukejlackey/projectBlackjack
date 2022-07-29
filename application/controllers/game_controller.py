from application import app, active_games, active_players
from application.models.game_model import Game
from flask import json, jsonify, request
from flask_cors import cross_origin

@app.route('/play/<int:user_id>', methods=['GET','POST'])
@cross_origin(origins="*", headers=['Content-type'])
def playGame(user_id):
    user_player = [player for player in active_players if player.user_id == int(user_id)]
    user_player = user_player[0]
    if user_id not in active_games:
        resp = json.loads(request.data.decode( 'UTF-8' ))
        active_games[user_id] = Game(user_player, num_of_players=int(resp['num_of_players'])+1)
    game = active_games[user_id]
    if game.stage is 0:
        return jsonify( game.showPlayers() ), 201
    elif game.stage is 1:
        return jsonify( game.startGame() ), 200
    elif game.stage is 2:
        resp = json.loads(request.data.decode( 'UTF-8' ))
        move = resp['move']
        print(move)
        return jsonify( game.runRound( move ) ), 201