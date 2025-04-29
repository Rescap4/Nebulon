from settings import *
from sprites import *

class Tablet(Sprite):
    def __init__(self, pos, surf, groups):
        Sprite.__init__(self, pos, surf, groups)
        self.surf = surf
        self.can_slide = False




