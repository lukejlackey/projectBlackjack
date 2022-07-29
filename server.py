from application import app
from application.controllers import user_controller, player_controller, game_controller

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000, debug=True)
 