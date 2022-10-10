import logging

class GamesSLL:
    def __init__(self):
        self.head = None
        
    def add_game_to_end(self, new_game):
        if self.head is None:
            self.head = new_game
            logging.debug(f'Game {new_game.game_id} added to active_games')
            return new_game
        game = self.head
        while game.next is not None:
            game = game.next
        game.next = new_game
        logging.debug(f'Game {new_game.game_id} added to active_games')
        return new_game

    def find_game_by_next_id(self, next_id):
        if self.head is None:
            logging.debug(f'Cannot find Game {next_id} in active_games')
            return False
        game = self.head
        if game.next is None:
            if game.game_id == next_id:
                logging.debug(f'Found only Game {next_id} in active_games')
                return (False, game)
            logging.debug(f'Cannot find Game {next_id} in active_games')
            return False
        while game.next is not None:
            if game.next is None:
                logging.debug(f'Cannot find Game {next_id} in active_games')
                return False
            if game.next.game_id == next_id:
                break
            game = game.next
        logging.debug(f'Found Games {game.game_id} and {next_id} in active_games')
        return (game, game.next)
    
    def remove_game_by_id(self, game_id):
        games = self.find_game_by_next_id(game_id)
        if games:
            prev_game, game = games
            if not prev_game:
                self.head = game.next
            else:
                prev_game.next = game.next
            logging.debug(f'Removed Game {game} from active_games')
            return True
        logging.debug(f'Game {game} is not in active_games, thus, it was not removed')
        return False
    
    def find_open_game(self):
        game = self.head
        while game is not None:
            if game.check_if_open():
                logging.debug(f'Found open game: Game {game.game_id}')
                return game
            game = game.next
        logging.debug('No open games!')
        return False

active_games = GamesSLL()
logging.debug('Created active_games')