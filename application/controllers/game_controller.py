from application import app, active_games, active_players
from application.models.game_model import Game
from application.models.player_model import Player
from flask import json, jsonify, request
from flask_cors import cross_origin

@app.route('/play/<int:user_id>', methods=['POST'])
@cross_origin(origins="*", headers=['Content-type'])
def createGame(user_id):
    user_player = list(filter(lambda player: player.user_id == int(user_id), active_players))
    if not user_player:
        Player.getPlayer(user_id=user_id)
        user_player = list(filter(lambda player: player.user_id == int(user_id), active_players))
    user_player = user_player[0]
    resp = json.loads(request.data.decode( 'UTF-8' ))
    active_games[user_id] = Game(user_player, num_of_players=int(resp['num_of_players'])+1)
    return jsonify({'game_created' : True}), 201
    
@app.route('/play/<int:user_id>/game', methods=['GET','POST'])
@cross_origin(origins="*", headers=['Content-type'])
def playGame(user_id):
    game = active_games[user_id]
    if game.stage == 0:
        return jsonify( game.showPlayers() ), 201
    if game.stage == 1:
        return jsonify( game.startGame() ), 200
    if game.stage == 2:
        resp = json.loads(request.data.decode( 'UTF-8' ))
        move = resp['move']
        return jsonify( game.runRound( move ) ), 201
    if game.stage == 3:
        return jsonify( game.gameOver() ), 200