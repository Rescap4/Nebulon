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
        self.level_complete()
        self.tablet_collected()
        
    def level_complete(self):
        if self.save.file_info.get(f'level_{self.level_num}') is False:
            self.image = pygame.mask.from_surface(self.image).to_surface()
            self.image.set_colorkey('black') # 'white' makes a cool effect
        else:
            mask = pygame.mask.from_surface(self.image)
            self.image = mask.to_surface(setcolor=(140, 140, 140, 250), unsetcolor=(0, 0, 0))
            self.image.set_colorkey('black')

    def tablet_collected(self):
        tablet_level = [0, 7, 18, 23, 24, 37, 38, 40]
        if int(self.level_num) in tablet_level:
            self.grid_pos = (int(self.pos[0] / TILE_SIZE), int(self.pos[1] / TILE_SIZE))
            line_y = self.image.get_height() - 16
            start_x = (self.image.get_width() - 32) // 2
            end_x = start_x + 32
            pygame.draw.line(self.image, (240, 240, 240), (start_x, line_y), (end_x, line_y), 2)

            # draw the line gray
            if self.save.file_info.get(f'tablet_{self.level_num}') is True:
                self.level_complete()
            
class Ground(Sprite):
    # created if the level contain the attribute
    def __init__(self, pos, surf, groups, color):
        Sprite.__init__(self, pos, surf, groups)
        self.color = color
        self.image = self.get_color_surf(surf)
        self.rect = self.image.get_rect(topleft=pos)
    
    def get_color_surf(self, surf):
        # Define the coordinates of each color block
        color_positions = {
            "pink": (0, 0),
            "green": (64, 0),
            "black": (128, 0),
            "orange": (0, 64),
            "blue": (64, 64),
            "gray": (128, 64),
        }

        if self.color in color_positions:
            x, y = color_positions[self.color]
            # Extract the corresponding 64x64 section of the image
            return surf.subsurface((x, y, 64, 64)).copy()
        else:
            raise ValueError(f"Invalid color: {self.color}. Available colors: {list(color_positions.keys())}")






