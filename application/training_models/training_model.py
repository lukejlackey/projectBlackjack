import matplotlib.pyplot as plt
import numpy as np
import names
from application.models.game_model import Game
from application.models.player_model import Player
from application import active_players

plt.ion()

ENEMY_BATCH_SIZE = 20

def createEnemies():
    for i in range(ENEMY_BATCH_SIZE):
        e = Player.createPlayer(names.get_full_name())
        Player.getPlayer(e)
    training_bots = [player for player in active_players if player.user_id == 0]
    for bot in training_bots:
        train(bot)

def train(player, render=False):
    if render:
        fig, ((record, reward_history), (q_table, results_bd)) = plt.subplots(2, 2)
        
        record.set_title( 'Record' )
        record.set_xlabel( 'Games Played' )
        record.set_ylabel( 'Average Result' )
        record.set(yticks=np.arange(0, 50, step=0.1))
        record.grid(True)
        record.axhline( y=player.epsilon/2, color='r', linestyle='dashed', label='Target' )
        rec_y = []
        
        reward_history.set_title( 'Reward History' )
        reward_history.set_xlabel( 'Learn Cycles' )
        reward_history.set_ylabel( 'Rewards' )
        reward_history.grid(True)
        reward_history.axhline( y=(player.epsilon*10)/2, color='r', linestyle='dashed', label='Target' )
        rh_y = []
        
        q_table.set_title( 'Q-Table' )
        q_table.set_xlabel( 'States' )
        q_table.set_ylabel( 'Q Values' )
        q_table.set(xticks=np.arange(player.STATE_MIN, player.STATE_MAX + 1, step=1))
        q_table.grid(True)
        
        results_bd.set_title( 'Results Breakdown' )
        results_bd_labels = list(player.RESULT_CODES.keys())
        results_bd_colors = list(plt.get_cmap('prism')(np.linspace(0.45, 0.85, len(results_bd_labels))))
        
        has_legend = False
        
        fig.tight_layout()
        plt.pause(3)
        plt.show()
        
    for episode in range( player.episodes ):
        training_game = Game( pl1=player, player_pool=training_dummies )
        record.set_title( f"Record (w/l ratio: {'%.3g' % (player.wl_ratio)})" )
        reward_history.set_title( f"Reward History (avg. reward: {'%.3g' % (sum(player.rewards)/len(player.rewards))})" )
        
        if episode % 25 == 0:
            plt.pause(1)
        
        fig.suptitle(f"Training Session (lvl: {player.skill_lvl} / eps: {'%.3g' % (player.epsilon)})")
        
        rec_y.append( player.wl_ratio )
        rec_x = range( len(rec_y) )
        record.plot( rec_x, rec_y, 'b', label='Win/Loss' )
        
        rh_y.append( sum(player.rewards)/len(player.rewards) )
        rh_x = range( len(rh_y) )
        reward_history.plot( rh_x, rh_y, 'y', label='Avg. Reward' )
        
        q_table.lines.clear()
        q_table.patches.clear()
        q_y1 = player.Q[:,0]
        q_y2 = player.Q[:,1]
        q_x = range( player.STATE_MIN, player.STATE_MAX + 1)
        q_table.bar( q_x, q_y1, color='c', width=-.4, align='edge', label='Hit' )
        q_table.bar( q_x, q_y2, color='m', width=.4, align='edge', label='Stand' )
        
        results_bd.texts.clear()
        results_bd.pie([getattr(player, a) for a in results_bd_labels], 
                        labels=results_bd_labels,
                        colors=results_bd_colors)
        
        if not has_legend:
            for sp in [record, reward_history, q_table]:
                sp.legend()
                has_legend = True
        
        plt.pause(.1)