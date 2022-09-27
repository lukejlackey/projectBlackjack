class ActiveGamesSLL:
    def __init__(self):
        self.head = None
        
    def add_game_to_end(self, new_game):
        if self.head is None:
            self.head = new_game
            return
        game = self.head
        while game.next is not None:
            game = game.next
        game.next = new_game
        return new_game

    def find_game_by_next_id(self, next_id):
        if self.head is None:
            return False
        game = self.head
        if game.next is None:
            if game.game_id == next_id:
                return (False, game)
            return False
        while game.next is not None:
            if game.next is None:
                return False
            if game.next.game_id == next_id:
                break
            game = game.next
        return (game, game.next)
    
    def remove_game_by_id(self, game_id):
        games = self.find_game_by_next_id(game_id)
        if games:
            prev_game, game = games
            if not prev_game:
                self.head = game.next
            else:
                prev_game.next = game.next
            return True
        return False
    
    def find_open_game(self):
        game = self.head
        while game is not None:
            if game.check_if_open():
                return game
        return False

active_games = ActiveGamesSLL()