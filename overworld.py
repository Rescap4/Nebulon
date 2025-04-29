from settings import *
from sprites import Sprite
from camera import Camera
from groups import AllSprites
from icon import Icon
from node import Node
from ast import literal_eval
from debug import *

class Overworld:
    def __init__(self, tmx_map, save, data, overworld_frames, audio, switch_level, screen_dimension):
        self.display_surface = pygame.display.get_surface()
        self.overworld_frames = overworld_frames

        self.switch_level = switch_level
        self.audio = audio
        self.save = save
        self.data = data
        self.update_flag = True

        # groups
        self.all_sprites = AllSprites()
        self.collision_sprites = pygame.sprite.Group()
        self.slide_objects = pygame.sprite.Group()
        self.node_sprites =  pygame.sprite.Group()

        self.current_node = 0 #[node for node in self.node_sprites if node.level == 0][0]


        self.load_assets()
        self.setup(tmx_map)
        self.background()

        # full screen
        self.screen_dimension = screen_dimension
        self.is_full_screen = False
        self.camera = self.camera1


    def load_assets(self):
        self.node_numbers = self.overworld_frames['node_numbers']
        self.icon_sprite = self.overworld_frames['icon']
        self.bg = self.overworld_frames['background']

    def setup(self, tmx_map):
        for x, y, image in tmx_map.get_layer_by_name('Decoration').tiles():
            Sprite((x * TILE_SIZE,y * TILE_SIZE), image, self.all_sprites)
        #for x, y, image in tmx_map.get_layer_by_name('Main').tiles():
        #    Sprite((x * TILE_SIZE,y * TILE_SIZE), image, (self.all_sprites, self.collision_sprites))

        for obj in tmx_map.get_layer_by_name('Triggers'):
            if obj.name == 'Camera1':
                self.camera1 = Camera((obj.x, obj.y))
            if obj.name == 'Camera2':
                self.camera2 = Camera((obj.x, obj.y))

        for obj in tmx_map.get_layer_by_name('Entities'):
            if obj.name == 'Stage':#and f'level_{int(obj.properties['level'])}' in self.save.file_info:
                self.node = Node((obj.x, obj.y), self.node_numbers[int(obj.properties['level'])], (self.all_sprites, self.node_sprites), self.save, self.data, obj.properties['level'])

        self.icon = Icon(literal_eval(self.save.file_info['icon_pos']), self.icon_sprite, self.all_sprites, self.collision_sprites, self.node_sprites, self.audio)
        
    def background(self):
        self.bg = pygame.transform.scale(self.bg, FULL_SCREEN_SIZE)
        self.bg_rect = self.bg.get_rect(center=self.display_surface.get_rect().center)

    def move_active(self):
        if self.update_flag: # only allow to move when menu closed
            self.icon.input()
            self.icon.animate()

    def input(self):
        keys = pygame.key.get_just_pressed()
        if self.update_flag: # only trigger when menu closed
            for node in self.node_sprites:
                if node.rect.colliderect(self.icon): 
                    self.data.current_level = int(node.level_num)
                    if keys[pygame.K_RETURN] and self.data.current_level in self.data.levels_imported:
                        self.audio.play_sfx('enter_b')
                        self.save.file_info['icon_pos'] = str(self.icon.pos)
                        self.switch_level('level', self.screen_dimension, 0)

                    if keys[pygame.K_g] or keys[pygame.K_t] or keys[pygame.K_u] or keys[pygame.K_i]:
                        self.audio.play_sfx('error_a')

    def run(self, dt):
        self.input()
        self.move_active()
        self.all_sprites.update(dt)

        self.display_surface.blit(self.bg, self.bg_rect)
        self.all_sprites.draw(self.camera.pos)


        #debug(f'size is {self.display_surface.get_size()}', 50)
        #debug(f'self.update_flag = {self.update_flag}', 50)