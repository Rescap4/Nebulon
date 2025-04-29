from settings import *
from sprites import Sprite
from camera import Camera
from groups import AllSprites
from icon import Icon
from node import Node

from debug import *


class Home:
    def __init__(self, tmx_map, save, data, home_frames, audio, switch_level, screen_dimension):
        self.display_surface = pygame.display.get_surface()
        self.save = save
        self.data = data
        self.audio = audio
        self.home_frames = home_frames
        self.switch_level = switch_level
        # groups
        self.all_sprites = AllSprites()
        
        self.load_assets()
        self.setup(tmx_map)
        self.background()

        # full screen
        self.screen_dimension = screen_dimension
        self.is_full_screen = False
        self.camera = self.camera1

    def load_assets(self):
        self.bg = self.home_frames['background']
        self.title = self.home_frames['title']

    def setup(self, tmx_map):
        for x, y, image in tmx_map.get_layer_by_name('Decoration').tiles():
            Sprite((x * TILE_SIZE,y * TILE_SIZE), image, self.all_sprites)
        #for x, y, image in tmx_map.get_layer_by_name('Main').tiles():
        #    Sprite((x * TILE_SIZE,y * TILE_SIZE), image, self.all_sprites)

        for obj in tmx_map.get_layer_by_name('Triggers'):
            if obj.name == 'Camera1':
                self.camera1 = Camera((obj.x, obj.y))
            if obj.name == 'Camera2':
                self.camera2 = Camera((obj.x, obj.y))

    def background(self):
        # bg
        self.bg = pygame.transform.scale(self.bg, FULL_SCREEN_SIZE)
        self.bg_rect = self.bg.get_rect(center=self.display_surface.get_rect().center)
        # title
        self.title = pygame.transform.scale(self.title, (WINDOW_HEIGHT, WINDOW_WIDTH))
        self.title_rect = self.title.get_rect(center=self.display_surface.get_rect().center)
        
    def input(self):
        keys = pygame.key.get_just_pressed()
        if keys[pygame.K_RETURN]:
            self.switch_level('map', 0)
            if self.switch_level('map', 0): # ensure the sound effect only plays when switch level succeds
                self.audio.play_sfx('enter_b')
        if keys[pygame.K_g] or keys[pygame.K_t] or keys[pygame.K_u] or keys[pygame.K_i]:
            self.audio.play_sfx('error_a')

    def run(self, dt):
        self.input()
        self.all_sprites.update(dt)

        self.display_surface.blit(self.bg, self.bg_rect)
        self.display_surface.blit(self.title, self.title_rect)
        self.all_sprites.draw(self.camera.pos)