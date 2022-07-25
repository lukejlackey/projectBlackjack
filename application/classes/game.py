import random
from classes.deck import Deck
from classes.player import Player

class Game:

    STARTING_HAND = 2

    def __init__( self, num_of_players, training_player=False ):
        self.num_of_players = num_of_players
        self.training_player = training_player
        self.deck = Deck()
        random.shuffle( self.deck.cards )
        self.addPlayers()
        self.playGame()

    def addPlayers( self ):
        self.players = []
        if not self.training_player:
            self.players.append( Player( isUser=True ) )
        else:
            self.players.append( self.training_player )
        self.players.append( random.sample(Player.ALL_PLAYERS, k=self.num_of_players - 1) )
        for i in range( len(self.players) ) :
            self.players[i].joinGame( seat=i )
        random.shuffle( self.players )

    def playGame( self ):
        i = 0
        self.players_out = 0
        self.dealCards( self.players*self.STARTING_HAND )
        while self.players_out < len( self.players ):
            if not self.players[i].out:
                self.takeTurn( self.players[i] )
            i = i + 1 if i < len( self.players ) else 0
        self.gameOver()

    def dealCards( self, *target ):
        for player in target:
            newCard = self.deck.cards.pop( 0 )
            player.cards.append( newCard )
            player.updateSelf()

    def takeTurn( self, plr ):
        move = plr.move()
        if move == 0:
            self.dealCards( [plr] )
        elif move == 1:
            plr.out = True
        self.players_out += plr.updateSelf( action=move )

    def gameOver(self):
        possible_winners = [player for player in self.players if player.count <= Player.MAX_SCORE]
        winning_score = max([player.count for player in possible_winners])
        self.winners = [player for player in possible_winners if player.count == winning_score]
        for player in self.players:
            if player not in self.winners:
                player.updateSelf( rslt=0 )
            elif player in self.winners:
                player.updateSelf( rslt=1 )