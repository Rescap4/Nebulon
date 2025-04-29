from settings import *
from sprites import *

class Grid(Sprite):
    def __init__(self, width, height, groups, save, color='darkgrey'):
        self.width = width
        self.height = height
        self.cell_size = 64
        self.save = save
        self.color = color
        self.surface = pygame.Surface((width, height), pygame.SRCALPHA)  # Transparent surface
        self.surface.fill((0, 0, 0, 0))  # Ensure full transparency
        self.draw_grid()

    def draw_grid(self):
        for i in range(self.cell_size, self.width, self.cell_size):
            pygame.draw.line(self.surface, self.color, (i, 0), (i, self.height), 1)
        for j in range(2 *self.cell_size, self.height, self.cell_size):
            pygame.draw.line(self.surface, self.color, (0, j), (self.width, j), 1)

    def draw(self, surface, offset):
        if self.save.file_info['grid']:
            surface.blit(self.surface, offset)