import numpy as np
import random

class Player:

    ALL_PLAYERS = []
    MAX_SCORE = 21
    ACTIONS = [0, 1]
    ACTION_SPACE = len( ACTIONS )
    STATE_MIN = 2
    STATE_MAX = 22
    STATES = [n for n in range( STATE_MIN, STATE_MIN )]
    STATE_SPACE = len( STATES )
    EPISODES = 5000
    NEW_Q_TABLE = np.zeros( ( STATE_SPACE, ACTION_SPACE ) )
    WIN_REWARD = 25
    LOSS_PENALTY = -25
    EPSILON_DECAY = .001
    SKILL_LEVELS = {
        '1' : {
            'epsilon' : 0.1,
            'l_rate' : 0.01,
            'gamma' : 0.01
        },
        '2' : {
            'epsilon' : 0.2,
            'l_rate' : 0.2,
            'gamma' : 0.2
        },
        '3' : {
            'epsilon' : 0.3,
            'l_rate' : 0.3,
            'gamma' : 0.3
        },
        '4' : {
            'epsilon' : 0.4,
            'l_rate' : 0.4,
            'gamma' : 0.4
        },
        '5' : {
            'epsilon' : 0.5,
            'l_rate' : 0.5,
            'gamma' : 0.5
        },
        '6' : {
            'epsilon' : 0.6,
            'l_rate' : 0.6,
            'gamma' : 0.6
        },
        '7' : {
            'epsilon' : 0.7,
            'l_rate' : 0.7,
            'gamma' : 0.7
        },
        '8' : {
            'epsilon' : 0.8,
            'l_rate' : 0.8,
            'gamma' : 0.8
        },
        '9' : {
            'epsilon' : 0.99,
            'l_rate' : 0.99,
            'gamma' : 0.99
        },
    }
    USER_STAT_CATEGORIES = ['wins', 'losses', 'blackjacks', 'busts']
    GAME_INIT_CATEGORIES = ['out', 'state', 'action', 'counter', 'next_state', 'result', 'reward']

    def __init__( self, isUser=False, name=None, avatar=0, q_table=NEW_Q_TABLE , skill_lvl=random.randint( 1, 9 ), rewards=0, user_stats=False ):
        self.isUser = isUser
        self.name = name
        self.avatar = avatar
        self.Q = q_table
        self.skill_lvl = skill_lvl
        self.rewards = rewards
        self.setLearnParams()
        self.setStats( user_stats )

    def setLearnParams( self ):
        for ( k, v ) in self.SKILL_LEVELS[str( self.skill_lvl )].items():
            setattr( self, k, v )

    def setStats( self, user_stats ):
        if user_stats:
            for ( k, v ) in user_stats.items():
                setattr( self, k, v )
        else:
            for s in self.USER_STAT_CATEGORIES:
                setattr( self, s, 0 )
        self.wl_ratio = self.wins / self.losses if self.losses else 1

    def joinGame( self, seat ):
        self.seat = seat
        self.cards = []
        for c in self.GAME_INIT_CATEGORIES:
            setattr( self, c, 0 )

    def updateScore( self ):
        self.state = self.counter - self.STATE_MIN
        self.counter = sum([card.value for card in self.cards])
        if self.counter > 21:
            self.busts += 1
            self.out = True
            self.result = 1
            self.next_state = self.STATE_MAX
            return 1
        elif self.counter == 21:
            self.blackjacks += 1
        self.next_state = self.counter - self.STATE_MIN
        return 0

    def updateSelf( self, action=None, rslt=None ):
        output = self.updateScore()
        if action is not None:
            self.action = action
            self.learn()
        if rslt is not None:
            self.result = rslt
            self.learn()
        self.state = self.next_state
        return output

    def giveReward( self ):
        if self.result is 0:
            self.reward = self.next_state
        elif self.result is 1:
            self.result = self.LOSS_PENALTY
            self.loses += 1
            self.wl_ratio = self.wins / self.losses
        elif self.result is 2:
            self.result = self.WIN_REWARD
            self.wins += 1
            self.wl_ratio = self.wins / self.losses if self.losses else 1

    def learn( self ):
        self.giveReward()
        self.Q[self.state, self.action] = self.Q[self.state, self.action] + self.l_rate * (self.reward + self.gamma * np.max(self.Q[self.next_state, :]) - self.Q[self.state, self.action])
        self.epsilon -= self.EPSILON_DECAY
        self.reward = 0

    def move( self, user_move=None ):
        if user_move is None:
            if np.random.uniform( 0, 1 ) < self.epsilon:
                action = random.choice( self.ACTIONS )
            else:
                action = np.argmax( self.Q[self.state, :] )
        else:
            action = user_move
        return action





    class PlayerAI():
        
        state_space = 19
        
        actions = [1,2]
        action_space = len(actions)
        
        win_reward = 25
        loss_penalty = -25
        
        def __init__(self) -> None:
            self.state = 0
            self.action = 0
            self.epsilon = 0.9
            self.EPISODES = 4200
            self.LEARNING_RATE = 0.02
            self.GAMMA = 0.98
            self.Q = np.zeros((self.state_space,self.action_space))
            self.total_rewards = []
            self.history = defaultdict(list)
        
        @staticmethod
        def shrink_number(num):
            return num - 3 if num < 21 else 18
        
        def pick_action(self, counter):
            counter = self.shrink_number(counter)
            if np.random.uniform(0, 1) < self.epsilon:
                action = random.choice(self.actions)
            else:
                action = np.argmax(self.Q[counter, :]) + 1
            self.action = action - 1
            self.history[str(counter)].append(action)
            x = [int(c) for c in self.history.keys()]
            self.hit_counts = [a.count(1) for a in self.history.values() if isinstance(a, list)]
            self.stand_counts = [a.count(2) for a in self.history.values() if isinstance(a, list)]
            if len(x) == 19:
                if hasattr(self, 'hcBar'):
                    for (b, ct) in [(self.hcBar, self.hit_counts), (self.scBar, self.stand_counts)]:
                        for rect, h in zip(b, ct):
                            rect.set_height(h)
                            plt.show()
                else:
                    self.hcBar = ax2.bar(x, self.hit_counts, width=1, edgecolor="white", linewidth=0.7, color='b', label='Hits')
                    self.scBar = ax2.bar(x, self.stand_counts, width=1, edgecolor="white", linewidth=0.7, color='r', label='Stands')
                    ax2.set_ylim([0, 500])
                    ax2.legend()
            return action
        
        def give_reward(self, counter, winner=None):
            counter = self.shrink_number(counter)
            if winner is False or counter >= self.state_space:
                reward = self.loss_penalty
            else:
                reward = counter
            self.total_rewards.append(reward)
            return reward
        
        def learn(self, counter, reward):
            state = self.shrink_number(self.state)
            counter = self.shrink_number(counter)
            self.Q[state, self.action] = self.Q[state, self.action] + self.LEARNING_RATE * (reward + self.GAMMA * np.max(self.Q[counter, :]) - self.Q[state, self.action])
            self.epsilon -= .0003