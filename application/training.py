import random
import matplotlib.pyplot as plt
import classes.player as plr
from game import Game, ax1



def train(player):
    ax1.set_ylabel('average rewards')
    ax1.set_xlabel('episodes')
    episodes = []
    rewards = []
    plt.pause(.2)
    plt.show()
    for episode in range(player.ai.EPISODES):
        training_game = Game(random.randint(2,9), player)
        episodes.append(episode)
        rewards.append(sum(player.ai.total_rewards)/len(player.ai.total_rewards))
        ax1.set_title(f'Epsilon: {player.ai.epsilon : .4f}')
        if episode % 25 == 0:
            print('-'*50)
            print(player.ai.Q)
            print('-'*50)
            ax1.plot(episodes, rewards, color='b', label='Test AI')
        plt.pause(.2)

testplayer = plr.Player()

train(testplayer)