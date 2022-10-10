import logging
import random
from threading import Timer
from application.classes.deck import Deck
from application.models.player_model import Player
from application import DATABASE
from application.classes.gamesSLL import active_games 
from application.classes.playersBST import ai_players, join_ai_players, join_idle_players
from application.config.mysqlconnection import connectToMySQL

class Game:

    TABLE_NAME = 'games'
    
    # Number of cards dealt to players at game start
    STARTING_HAND = 2
    
    NUM_OF_PLAYERS = 8

    #Constructor
    def __init__( self):
        logging.debug('Creating game')
        self.next = None
        self.player_pool = ai_players if len(ai_players) >= self.NUM_OF_PLAYERS else Player.get_random_players()
        self.game_id = game_count
        game_count += 1
        self.turn = 0
        self.deck = Deck()
        random.shuffle( self.deck.cards )
        self.players = []
        self.start_game_lobby_timer()
        logging.debug(f'Created game {self.game_id}')
        
    #Start timer to await user players, otherwise fill with A.I.
    def start_game_lobby_timer( self ):
        active_games.add_game_to_end(self)
        t = Timer(10,self.fill_players())
        t.start()
        logging.debug(f'Game {self.game_id} lobby timer started')

    def check_if_open(self):
        return True if len(self.players) < self.NUM_OF_PLAYERS else False

    # Add a players to the game
    def add_player( self, player ):
        if self.check_if_open():
            self.players.append( player )
            player.join_game(seat=len(self.players)-1)
            logging.debug(f'Player {player.p_id} joined Game {self.game_id}')
            return True
        logging.debug(f'Player {player.p_id} could not join Game {self.game_id}: lobby full')
        return False

    # Delete game if no players joined or fill empty spots with A.I.
    def fill_players( self ):
        players_needed = self.NUM_OF_PLAYERS - len(self.players)
        if self.check_if_open():
            players = ai_players.get_players(players_needed)
            players_needed = players_needed - len(players)
            if players_needed:
                extra_players = Player.get_random_players(players_needed)
                players.extend(extra_players)
            for player in players:
                self.add_player(player)
            logging.debug(f'Game {self.game_id}: filled lobby with A.I. players')
            return True
        return False

    # Returns info about all players in game
    def show_players( self ):
        return {'players' : [player.display_values for player in self.players]}

    # Deal initial hands
    def start_game( self ):
        self.record_game()
        logging.debug(f'Game {self.game_id}: starting')
        cards = self.deal_cards( self.players*self.STARTING_HAND )
        return {'cards': cards}

    # Deals 1 card to each player and updates their attributes
    def deal_cards( self, target_list):
        for player in target_list:
            newCard = self.deck.cards.pop( 0 )
            player.cards.append( newCard )
            logging.debug(f'Game {self.game_id}: Player {player.p_id} dealt card {newCard.info_str}')
            player.updateSelf()
        cards = {}
        for player in self.players:
            cards[str(player.seat)] = [c.info for c in player.cards]
        return cards

    # Receives player move (Hit = 0 / Stand = 1), dealing a card if their move is 0, or setting the player's 'out' status to true if move is 1 or player busts 
    def take_turn( self, plr, move=None):
        if(plr.seat != self.turn):
            return None
        move = move if move is not None else plr.move()
        if move == 0:
            logging.debug(f'Game {self.game_id}: Player {plr.p_id} hits')
            self.deal_cards( [plr] )
        elif move == 1:
            logging.debug(f'Game {self.game_id}: Player {plr.p_id} stands')
            plr.out = True
        plr.updateSelf( action=move )
        next_player = self.to_next_turn()
        game_over_counter = 1
        while next_player.out:
            next_player = self.to_next_turn()
            game_over_counter += 1
            if game_over_counter > self.NUM_OF_PLAYERS:
                return self.game_over()
        if not next_player.out and 'user_id' not in next_player:
            self.take_turn(next_player)
        return self.turn
    
    def to_next_turn(self):
        next_turn = self.turn + 1
        self.turn = next_turn if next_turn < self.NUM_OF_PLAYERS else 0
        next_player = self.players[self.turn]
        return next_player
    
    @staticmethod
    def update_plus_append_result(player, result_code, game_data):
        player.update_self( rslt= Player.RESULT_CODES[result_code])
        if 'user_id' in player:
            join_idle_players(player)
        else:
            join_ai_players(player)
        game_data['players'][player.seat]['result'] = player.result
        return game_data

    # Determines winners/losers
    def game_over(self):
        logging.debug(f'Game {self.game_id}: GAME OVER')
        game_data = self.show_players()
        possible_winners = [player for player in self.players if player.counter <= Player.MAX_SCORE]
        if possible_winners:
            winning_score = max([player.counter for player in possible_winners])
        else:
            winning_score = None
        winners = [player for player in possible_winners if player.counter == winning_score]
        game_data['winning_score'] = winning_score
        for player in self.players:
            game_data = self.update_plus_append_result(player, 'wins' if player in winners else 'losses', game_data )
        return game_data
    
    def record_game(self):
        query = f"INSERT INTO {self.TABLE_NAME} DEFAULT VALUES;"
        self.db_id = connectToMySQL(DATABASE).query_db(query)
        return self.db_id

    
    def record_result(self, player, result):
        query = f"INSERT INTO {Player.RESULT_TABLES[result]} (game_id, player_id) "
        query += f"VALUES( {self.db_id}, {player.p_id} );"
        rslt = connectToMySQL(DATABASE).query_db(query)
        return rslt