from application import app, DATABASE, active_players
from application.config.mysqlconnection import connectToMySQL
from copy import deepcopy
import numpy as np
import random
import names

class Player:

    # MySQL
    TABLE_NAME = 'players'
    Q_SQL_TABLE = 'q_tables'
    WIN_TABLE = 'games_have_winners'
    LOSS_TABLE = 'games_have_losers'
    BLACKJACK_TABLE = 'games_have_blackjacks'
    BUST_TABLE = 'games_have_busts'
    RESULT_TABLES = {
        'wins' : WIN_TABLE,
        'losses' : LOSS_TABLE,
        'blackjacks' : BLACKJACK_TABLE,
        'busts' : BUST_TABLE
    }
    
    #Player attributes
    ATTR_TAGS = ['name', 'avatar', 'skill_lvl', 'user_id']
    DISPLAY_TAGS = ['seat', 'cards', 'user_id', 'name', 'avatar', 'skill_lvl', 'wins', 'losses', 'blackjacks', 'busts', 'wl_ratio']
    
    #On new game reset
    GAME_INIT_CATEGORIES = ['out', 'state', 'action', 'counter', 'next_state', 'result', 'reward']
    
    # A.I. Actions
    ACTIONS = [0, 1]
    ACTION_SPACE = len( ACTIONS )
    
    #A.I. States
    MAX_SCORE = 21
    STATE_MIN = 2
    STATE_MAX = MAX_SCORE + 1
    STATE_ADJUSTMENT = STATE_MIN + 1
    OVER_STATE = STATE_MAX - STATE_ADJUSTMENT
    STATES = list(range( 0, STATE_MAX - 1))
    STATE_SPACE = len( STATES )
    
    #A.I. Agent/Training params
    EPISODES = 1000
    EPSILON = .99
    EPSILON_DECAY = .0005
    NEW_Q_TABLE = np.zeros( ( STATE_SPACE, ACTION_SPACE ) )
    SKILL_LEVELS = {
        '1' : {
            'l_rate' : 0.99,
            'gamma' : 0.01
        },
        '2' : {
            'l_rate' : 0.88,
            'gamma' : 0.2
        },
        '3' : {
            'l_rate' : 0.77,
            'gamma' : 0.3
        },
        '4' : {
            'l_rate' : 0.66,
            'gamma' : 0.4
        },
        '5' : {
            'l_rate' : 0.5,
            'gamma' : 0.5
        },
        '6' : {
            'l_rate' : 0.44,
            'gamma' : 0.6
        },
        '7' : {
            'l_rate' : 0.33,
            'gamma' : 0.7
        },
        '8' : {
            'l_rate' : 0.22,
            'gamma' : 0.8
        },
        '9' : {
            'l_rate' : 0.09,
            'gamma' : 0.98
        },
    }
    
    # A.I. Rewards/Penalties
    WIN_REWARD = 25
    BLACKJACK_REWARD = 30
    LOSS_PENALTY = -25
    BUST_PENALTY = -30
    RESULT_CODES = {
        'losses' : 1,
        'busts' : 2,
        'wins' : 3,
        'blackjacks' : 4
    }
    RESULT_REWARDS = {
        '1' : LOSS_PENALTY,
        '2' : BUST_PENALTY,
        '3' : WIN_REWARD,
        '4' : BLACKJACK_REWARD
    }

    #Constructor
    def __init__( self, p_id=None, user_id=None, name=None, avatar=None, q_table=None, skill_lvl=None, wins=0, losses=0, busts=0, blackjacks=0):
        self.p_id = p_id if p_id is not None else 0
        self.user_id = user_id if user_id is not None else -1
        self.name = name if name is not None else names.get_full_name()
        self.avatar = avatar if avatar is not None else 0
        self.Q = q_table if q_table is not None else deepcopy(self.NEW_Q_TABLE)
        self.skill_lvl = skill_lvl if skill_lvl is not None else random.randint( 1, 9 )
        self.record = [1] * int(losses) + [2] * int(busts) + [3] * int(wins) + [4] * int(blackjacks)
        self.display_values = {}
        self.cards = []
        self.seat = 0
        self.set_learn_params()
        self.update_record()

    # Set A.I. learning parameters according to skill level
    def set_learn_params( self ):
        for ( k, v ) in self.SKILL_LEVELS[str( self.skill_lvl )].items():
            setattr( self, k, v )
        self.episodes = self.EPISODES * self.skill_lvl
        self.epsilon = self.EPSILON
        self.rewards = []

    # Updates player record
    def update_record( self ):
        for (k, v) in self.RESULT_CODES.items():
            setattr(self, k, self.record.count(v))
        self.wl_ratio = '%.2g' %((self.wins + self.blackjacks) / (self.losses + self.busts)) if (self.losses + self.busts) else 1
        self.games_played = len(self.record)
        self.update_display_values()

    # Updates player display values for front end display
    def update_display_values( self ):
        for tag in self.DISPLAY_TAGS:
            self.display_values[tag] = getattr(self, tag)

    # Join new game
    def join_game( self, seat ):
        self.seat = seat
        self.cards = []
        for c in self.GAME_INIT_CATEGORIES:
            setattr( self, c, 0 )
        self.update_record()

    # Allow A.I. to make move if not controlled by player
    def move( self, user_move=None ):
        if user_move is None:
            if np.random.uniform( 0, 1 ) < self.epsilon:
                action = random.choice( self.ACTIONS )
            else:
                action = np.argmax( self.Q[self.state, :] )
        else:
            action = user_move
        return action

    # Update score after card is dealt
    def updateScore( self ):
        self.state = self.counter - self.STATE_ADJUSTMENT if self.counter - self.STATE_ADJUSTMENT < self.OVER_STATE else self.OVER_STATE
        self.counter = sum([card.point_val for card in self.cards])
        if self.counter > self.MAX_SCORE:
            self.out = True
            self.result = 2
            self.next_state = self.OVER_STATE
            return 1
        elif self.counter == self.MAX_SCORE - self.STATE_ADJUSTMENT:
            self.out = True
            self.result = 4
        self.next_state = self.counter - self.STATE_MIN
        return 0 if not self.out else 1

    # Update A.I. state/action/reward values
    def updateSelf( self, action=None, rslt=None ):
        output = self.updateScore()
        if action is not None:
            self.action = action
            self.learn()
            self.update_display_values()
        if rslt is not None:
            self.result = rslt if self.result is 0 else self.result
            self.learn()
            self.record.append( self.result )
            self.update_record()
        self.state = self.next_state
        return output

    # Provide reward value based on state
    def giveReward( self ):
        if self.result is 0:
            self.reward = self.next_state
        else:
            self.reward = self.RESULT_REWARDS[str(self.result)]
        self.rewards.append( self.reward )

    # Train A.I. with basic RL model
    def learn( self ):
        self.giveReward()
        self.Q[self.state, self.action] = self.Q[self.state, self.action] + self.l_rate * (self.reward + self.gamma * np.max(self.Q[self.next_state, :]) - self.Q[self.state, self.action])
        self.epsilon -= self.EPSILON_DECAY
        self.reward = 0

    #Create new player
    @classmethod
    def createPlayer( cls, name, user_id=0 ):
        new_player = cls( name=name, user_id=1 if user_id else user_id)
        player_data = {}
        for tag in cls.ATTR_TAGS:
            player_data[tag] = getattr(new_player, tag)
        query = f"INSERT INTO {cls.TABLE_NAME}( {', '.join(cls.ATTR_TAGS)} ) "
        cols = []
        for tag in cls.ATTR_TAGS:
            cols.append( f'%({tag})s' )
        cols = ', '.join(cols)
        query += f'VALUES( {cols} );'
        print(query)
        rslt = connectToMySQL(DATABASE).query_db(query, player_data)
        print(rslt)
        cls.saveQTable( new_player, rslt)
        return rslt

    #Retrieve Player from MySQL database
    @classmethod
    def get_player( cls, user_id ):
        query = f"SELECT {cls.TABLE_NAME}.id AS p_id, name, avatar, skill_lvl, COUNT(wins.player_id) AS wins, COUNT(losses.player_id) AS losses, COUNT(blackjacks.player_id) AS blackjacks, COUNT(busts.player_id) AS busts "
        query += f"FROM {cls.TABLE_NAME} "
        query += f"LEFT JOIN {cls.WIN_TABLE} AS wins ON {cls.TABLE_NAME}.id = wins.player_id "
        query += f"LEFT JOIN {cls.LOSS_TABLE} AS losses ON {cls.TABLE_NAME}.id = losses.player_id "
        query += f"LEFT JOIN {cls.BLACKJACK_TABLE} AS blackjacks ON {cls.TABLE_NAME}.id = blackjacks.player_id "
        query += f"LEFT JOIN {cls.BUST_TABLE} AS busts ON {cls.TABLE_NAME}.id = busts.player_id "
        query += f'WHERE {cls.TABLE_NAME}.id = {user_id};'
        rslt = connectToMySQL(DATABASE).query_db(query)
        print(rslt[0])
        plr = cls(**rslt[0])
        plr.user_id = user_id
        plr.Q = cls.getQTable(plr.p_id)
        active_players.append(plr)
        return rslt[0] if rslt else False
    
    #Save A.I. Q-table array
    @staticmethod
    def saveQTable( plr, plr_id ):
        qpath = r"C:\Users\lukej\OneDrive\Desktop\Coding\CodingDojo\projects\projectBlackjack\q_tables\Q" + str(plr_id)
        q = np.save(qpath, plr.Q)
        return q

    #Retrieve A.I. Q-table array
    @staticmethod
    def getQTable( plr_id ):
        qpath = r"C:\Users\lukej\OneDrive\Desktop\Coding\CodingDojo\projects\projectBlackjack\q_tables\Q" + str(plr_id) + '.npy'
        q = np.load(qpath)
        return q