from application import app, active_users
from application.models.user_model import User
from application.models.player_model import Player
from flask import json, jsonify, request, session
from flask_cors import cross_origin
import secrets

@app.route('/login', methods=['POST'])
@cross_origin(origins="*", headers=['Content-type'])
def loginProcess():
    recv_data = json.loads(request.data.decode( 'UTF-8' ))
    user_data = User.validateLogin(recv_data)
    print(user_data)
    if user_data["logged_user"]:
        user_data["logged_user"]["token"] = secrets.token_urlsafe(17)
        active_users[f'{user_data["logged_user"]["p_id"]}'] = user_data["logged_user"]['token']
    return jsonify( user_data ), 201

@app.route('/register', methods=['POST'])
@cross_origin(origins="*", headers=['Content-type'])
def registerProcess():
    recv_data = json.loads(request.data.decode( 'UTF-8' ))
    user_data = User.registerNewUser(recv_data)
    if user_data["logged_user"]:
        user_data["logged_user"]["token"] = secrets.token_urlsafe(17)
        active_users[f'{user_data["logged_user"]["p_id"]}'] = user_data["logged_user"]['token']
    return jsonify( user_data ), 201

@app.route('/update', methods=['POST'])
@cross_origin(origins="*", headers=['Content-type'])
def updateProcess():
    recv_data = json.loads(request.data.decode( 'UTF-8' ))
    user_data = {'error' : 'Please log back in'}
    if recv_data["user_id"] not in active_users:
        return jsonify( user_data ), 201
    if recv_data["token"] == active_users[recv_data["user_id"]]:
        user_data = { "logged_user" : Player.getPlayer(user_id=recv_data['user_id'])}
    return jsonify( user_data ), 201