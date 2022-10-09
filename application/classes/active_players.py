class ActivePlayersBST:
    def __init__(self):
        self.root = None
    
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
        return curr
    
    def remove_player(self, player, recursive_curr=None):
        curr = recursive_curr if recursive_curr is not None else self.root
        if curr is None:
            if self.root is None:
                self.root = player
                return player
            
    def find_min_player_id_player(self, start_from=None):
        curr = start_from if start_from is not None else self.root
        while(curr.left is not None):
            curr = curr.left
        return curr
            
    def search_for_player(self, player, recursive_curr=None):
        curr = recursive_curr if recursive_curr is not None else self.root
        if curr is None:
            return False
        if curr.p_id < player.p_id:
            return self.search_for_player(player, curr.right)
        elif curr.p_id > player.p_id:
            return self.search_for_player(player, curr.left)
        else:
            return curr