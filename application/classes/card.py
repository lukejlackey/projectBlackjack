class Card:

    def __init__( self , suit , point_val , string_val ):
        
        self.suit = suit
        self.point_val = point_val
        self.string_val = string_val
        self.info = {
            'suit' : suit,
            'point_val' : point_val,
            'string_val' : string_val
        }
        self.info_str = f"{self.string_val} of {self.suit} : {self.point_val} points"