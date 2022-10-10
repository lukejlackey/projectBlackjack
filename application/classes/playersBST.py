import logging

class PlayersBST:
    def __init__(self, name):
        self.root = None
        self.name = name
    
    def add_player(self, player, recursive_curr=None):
        curr = recursive_curr if recursive_curr is not None else self.root
        if curr is None:
            if self.root is None:
                self.root = player
            return player
        if curr.p_id < player.p_id:
            curr.right = self.add_player(player, curr.right)
        elif curr.p_id > player.p_id:
            curr.left = self.add_player(player, curr.left)
        logging.debug(f'Player {player.p_id} added to {self.name}')
        return curr
    
    def search_for_player(self, player_id, remove=False, recursive_curr=None):
        curr = recursive_curr if recursive_curr is not None else self.root
        if curr is None:
            logging.debug(f'Player not in {self.name}!')
            return False
        if curr.p_id < player_id:
            return self.search_for_player(player_id, remove, curr.right)
        elif curr.p_id > player_id:
            return self.search_for_player(player_id, remove, curr.left)
        else:
            if not remove:
                logging.debug(f'Player {player_id} found in {self.name}')
                return curr
            if curr.right and curr.left: 
                [parent, child] = self.find_min_succ(curr.right, curr)
                if parent.left == child:
                    parent.left = child.right
                else:
                    parent.right = child.right
                child.left = curr.left
                child.right = curr.right
                parent.left = parent.right = None
                logging.debug(f'Player {player_id} removed from {self.name}')
                return child
            if curr.left:
                logging.debug(f'Player {player_id} removed from {self.name}')
                return curr.left
            else:
                logging.debug(f'Player {player_id} removed from {self.name}')
                return curr.right

    def find_min_succ(self, player, parent):
        if player.left:
            return self.find_min_succ(player.left, player)
        return [parent, player]
    
    def find_max_succ(self, player, parent):
        if player.right:
            return self.find_max_succ(player.right, player)
        return [parent, player]
    
    def get_players(self, players_needed):
        players = []
        player = self.root
        while player is not None or len(players) == players_needed:
            removed_player = self.search_for_player(player.p_id, remove=True)
            if removed_player:
                players.append(removed_player)
            player = self.root
        return players
    
    def count(self, player=None):
        player = player if player is not None else self.root
        if player is None:
            return 0
        return 1 + self.count(player.left) + self.count(player.right)
    
idle_players = PlayersBST('idle_players')
active_players = PlayersBST('active_players')
ai_players = PlayersBST('ai_players')

logging.debug('Created idle_players, active_players, and ai_players')

def change_trees(player, prev_tree, new_tree):
    prev_tree.search_for_player(player.p_id, remove=True)
    new_tree.add_player(player)
    logging.debug(f'Player moved from {prev_tree.name} to {new_tree.name}')

def join_idle_players(player):
    change_trees(player, active_players, idle_players)
    
def join_active_players(player):
    change_trees(player, idle_players, active_players)

def join_ai_players(player):
    change_trees(player, idle_players, ai_players)