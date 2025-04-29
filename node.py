from settings import *
from sprites import Sprite

class Node(Sprite):
    def __init__(self, pos, surf, groups, save, data, level_num):
        Sprite.__init__(self, pos, surf, groups)

        self.level_num = level_num
        self.save = save
        self.data = data
        self.pos = pos

        self.image = surf.copy()

        self.tablet_collected()
        self.level_complete()

    def tablet_collected(self):
        tablet_level = [7, 15, 23, 29, 37, 40]
        if int(self.level_num) in tablet_level:
            if not self.save.file_info.get(f'tablet_{self.level_num}') is True:
                self.grid_pos = (int(self.pos[0] / TILE_SIZE), int(self.pos[1] / TILE_SIZE))

                line_y = self.image.get_height() - 16
                start_x = (self.image.get_width() - 32) // 2
                end_x = start_x + 32
                pygame.draw.line(self.image, (240, 240, 240), (start_x, line_y), (end_x, line_y), 2)


    def level_complete(self):
        if self.save.file_info.get(f'level_{self.level_num}') is False:
            self.image = pygame.mask.from_surface(self.image).to_surface()
            self.image.set_colorkey('black') # 'white' makes a cool effect
        else:
            mask = pygame.mask.from_surface(self.image)
            self.image = mask.to_surface(setcolor=(140, 140, 140, 250), unsetcolor=(0, 0, 0))
            self.image.set_colorkey('black')
            



