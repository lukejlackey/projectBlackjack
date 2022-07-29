from application import app
from application.models.user_model import User
from application.models.player_model import Player
from flask import json, jsonify, request, session
from flask_cors import cross_origin

@app.route('/login', methods=['POST'])
@cross_origin(origins="*", headers=['Content-type'])
def loginProcess():
    recv_data = json.loads(request.data.decode( 'UTF-8' ))
    user_data = User.validateLogin(recv_data)
    return jsonify( user_data ), 201

@app.route('/register', methods=['POST'])
@cross_origin(origins="*", headers=['Content-type'])
def registerProcess():
    recv_data = json.loads(request.data.decode( 'UTF-8' ))
    user_data = User.registerNewUser(recv_data)
    return jsonify( user_data ), 201