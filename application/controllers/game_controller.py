from application import app, active_games, active_players, socketio
from application.models.game_model import Game
from application.models.player_model import Player
from flask import json, jsonify, request
from flask_cors import cross_origin
from flask_socketio import join_room, leave_room

def find_active_players_with_id(user_id):
    matches = list(filter(lambda player: player.user_id == int(user_id), active_players))
    return matches

# @app.route('/play/<int:user_id>', methods=['POST'])
# @cross_origin(origins="*", headers=['Content-type'])
# def create_game(user_id):
#     user_player = find_active_players_with_id(user_id)
#     if not user_player:
#         plyr = Player.get_player(user_id=user_id)
#         user_player = find_active_players_with_id(user_id)
#     user_player = user_player[0]
#     resp = json.loads(request.data.decode( 'UTF-8' ))
#     active_games[user_id] = Game(user_player, num_of_players=int(resp['num_of_players'])+1)
#     return jsonify({'game_created' : True}), 201
    
# @app.route('/play/<int:user_id>/game', methods=['GET'])
# @cross_origin(origins="*", headers=['Content-type'])
# def getGameData(user_id):
#     game = active_games[user_id]
#     if game.stage == 0:
#         return jsonify( game.showPlayers() ), 201
#     if game.stage == 1:
#         return jsonify( game.startGame() ), 200
#     if game.stage == 2:
#         resp = json.loads(request.data.decode( 'UTF-8' ))
#         move = resp['move']
#         return jsonify( game.runRound( move ) ), 201
#     if game.stage == 3:
#         return jsonify( game.gameOver() ), 200

# @app.route('/play/<int:user_id>/game', methods=['POST'])
# @cross_origin(origins="*", headers=['Content-type'])
# def playGame(user_id):
#     game = active_games[user_id]
#     if game.stage == 0:
#         return jsonify( game.showPlayers() ), 201
#     if game.stage == 1:
#         return jsonify( game.startGame() ), 200
#     if game.stage == 2:
#         resp = json.loads(request.data.decode( 'UTF-8' ))
#         move = resp['move']
#         return jsonify( game.runRound( move ) ), 201
#     if game.stage == 3:
#         return jsonify( game.gameOver() ), 200

@app.route('/play/<int:user_id>', methods=['POST'])
@cross_origin(origins="*", headers=['Content-type'])
def create_game(user_id):
    user_player = find_active_players_with_id(user_id)
    if not user_player:
        plyr = Player.get_player(user_id=user_id)
        user_player = find_active_players_with_id(user_id)
    user_player = user_player[0]
    new_game = Game()
    new_game.add_player(user_player)
    return jsonify({
        'game_created' : True,
        'game_id' : new_game.game_id
        }), 201

@socketio.on('join', namespace='/game')
def join_game(request):
    response = json.loads(request.data.decode( 'UTF-8' ))
    user_id = response['userId']
    game_id = response['gameId']
    user_player = find_active_players_with_id(user_id)
    if not user_player:
        plyr = Player.get_player(user_id=user_id)
        user_player = find_active_players_with_id(user_id)
    user_player = user_player[0]
    game = active_games.find_open_game()
    if not game:
        game = active_games.add_game_to_end(Game())
    game.add_player(user_player)
    join_room(game_id)
    emit('joined_user',jsonify(user_player.display_values), to=game_id)

@socketio.on('move', namespace='/game')
def make_move(request):
    response = json.loads(request.data.decode( 'UTF-8' ))
    user_id = response['userId']
    user_move = response['userMove']
    game_id = response['gameId']
    user_player = find_active_players_with_id(user_id)
    if not user_player:
        plyr = Player.get_player(user_id=user_id)
        user_player = find_active_players_with_id(user_id)
    user_player = user_player[0]
    game = Game.find_game_by_game_id(game_id)
    game_data = game.take_turn(user_player, user_move)
    if type(game_data) == int:
        game_data = {
            'game_data' : game.show_players(),
            'next_turn' : game_data
        }
    emit('game_data',jsonify(game_data), to=game_id)
