import random
from application.classes.deck import Deck
from application.models.player_model import Player
from application import active_players

training_dummies = []
for i in range(10):
    training_dummies.append(Player(p_id=0-i))

class Game:

    STARTING_HAND = 2

    def __init__( self, pl1, num_of_players=random.randint(2,9), player_pool=active_players):
        self.num_of_players = num_of_players
        self.pl1 = pl1
        self.player_pool = player_pool
        self.stage = 0
        self.deck = Deck()
        random.shuffle( self.deck.cards )
        self.addPlayers()

    def addPlayers( self ):
        self.players = []
        self.players.append( self.pl1 )
        self.players.extend( random.sample(training_dummies, self.num_of_players - 1) )
        random.shuffle( self.players )
        for i in range( len(self.players) ) :
            self.players[i].joinGame( seat=i+1 )

    def showPlayers( self ):
        self.stage += 1
        return {'players' : [player.display_values for player in self.players]}

    def startGame( self ):
        self.stage += 1
        self.turn = 0
        self.players_out = 0
        rv = self.dealCards( self.players*self.STARTING_HAND, initDeal=True )
        print(rv)
        return rv

    def dealCards( self, target, initDeal=False ):
        for player in target:
            newCard = self.deck.cards.pop( 0 )
            player.cards.append( newCard )
            player.updateSelf()
        cards = {}
        for player in self.players:
            cards[str(player.seat)] = [c.info for c in player.cards[1:]] if player != self.pl1 and initDeal else [c.info for c in player.cards]
        return cards

    def runRound( self, pl1_move=False ):
        cards = {'game_over': False}
        self.turn = 0
        while self.turn < len(self.players):
            current_player = self.players[self.turn]
            print("turn " + str(self.turn + 1))
            print(current_player.out)
            if not current_player.out:
                if self.turn + 1 == self.pl1.seat:
                    print("took p1 turn")
                    card = self.takeTurn(current_player, pl1_move)
                else:
                    card = self.takeTurn(current_player)
                if card:
                    cards[str(self.turn + 1)] = card
            self.turn = self.turn + 1
        if len(cards.keys()) == 1:
            cards['game_over'] = True
            self.stage += 1
        return cards

    def takeTurn( self, plr, move=None ):
        move = move if move is not None else plr.move()
        if move == 0:
            self.dealCards( [plr] )
            card = plr.cards[-1].info
        elif move == 1:
            plr.out = True
            card = False
        self.players_out += plr.updateSelf( action=move )
        print(plr.seat, move)
        return card

    def gameOver(self):
        possible_winners = [player for player in self.players if player.counter <= Player.MAX_SCORE]
        if possible_winners:
            winning_score = max([player.counter for player in possible_winners])
        else:
            winning_score = None
        self.winners = [player for player in possible_winners if player.counter == winning_score]
        game_data = {'winning_score' : winning_score}
        for player in self.players:
            if player not in self.winners:
                player.updateSelf( rslt=1 )
                game_data[str(player.seat)] = 0
            elif player in self.winners:
                player.updateSelf( rslt=3 )
                game_data[str(player.seat)] = 1
        return game_data