import logging
from application import app
from application.controllers import user_controller, player_controller, game_controller

host = '127.0.0.1'
port = 5000

if __name__ == '__main__':
    app.run(host=host, port=port, debug=True)
    logging.debug(f'App started at {host} on port {port}')
 