from application.classes.player import Player
from classes.game import Game

def train(player, render=False):
    for episode in range(Player.EPISODES):
        training_game = Game(training_player=player)

testplayer = Player()

train( testplayer )