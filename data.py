from settings import *

class Data:
    def __init__(self):
        self.unlocked_level = 0 # need to be saved
        self.current_level = 0 # should reset
        #self.icon_pos = (512, 704) # position of the level 0 (can reset)

        self.levels_imported = [] # should reset