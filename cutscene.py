
from settings import *
from sprites import Sprite
from player import Player
from groups import AllSprites
from support import * 
from timers import Timer
from camera import Camera   
#from history import History
from debug import *
#from battery import Battery
#from tablet import Tablet
#from spike import Spike
#from box import Box
#from grid import Grid
from particle import Particle, SlideParticle


## Level class will contain all the method of the game so far
class Cutscene:
    def __init__(self, tmx_map, save, data, cutscene_frames, audio, switch_level, screen_dimension):
        self.display_surface = pygame.display.get_surface()
        self.clock = pygame.time.Clock()
        self.save = save
        self.data = data
        self.audio = audio
        self.switch_level = switch_level
        self.cutscene_frames = cutscene_frames
        self.screen_dimension = screen_dimension

        # groups (maybe not of them need to be loaded every level)
        self.all_sprites = AllSprites()
        self.collision_sprites = pygame.sprite.Group()
        self.player_sprites = pygame.sprite.Group()
        self.spike_sprites = pygame.sprite.Group()
        self.battery_sprites = pygame.sprite.Group()
        self.tablet_sprites = pygame.sprite.Group()
        self.box_sprites = pygame.sprite.Group()
        self.exit_sprites = pygame.sprite.Group()
        self.game_objects = pygame.sprite.Group()
        self.slide_objects = pygame.sprite.Group()
        self.link_sprites = pygame.sprite.Group()

        # load level   
        self.load_assets(cutscene_frames)
        self.setup(tmx_map)
        self.create_assets()
        self.background()
        self.timer_setup()

        # General variables
        self.active_player_index = 0
        self.camera = self.camera1

        self.audio.stop_all()
        pygame.mixer.music.stop()


    def load_assets(self, cutscene_frames):
        self.player_frames = cutscene_frames['player']

    def create_assets(self):
        # create particles
        self.PARTICLE_EVENT = pygame.USEREVENT + 1
        pygame.time.set_timer(self.PARTICLE_EVENT, 10)
        self.particle1 = Particle((0, 0), self.all_sprites, self.screen_dimension)
        self.particle2 = SlideParticle((0, 0), self.all_sprites, self.screen_dimension)
        self.particle_event_timer = Timer(10, self.particle_event, True, True)

    def setup(self, tmx_map):
        self.level_width = tmx_map.width * TILE_SIZE
        self.level_height = tmx_map.height * TILE_SIZE

        for x, y, image in tmx_map.get_layer_by_name('Decoration').tiles():
            Sprite((x * TILE_SIZE,y * TILE_SIZE), image, self.all_sprites)

        for x, y, image in tmx_map.get_layer_by_name('Main').tiles():
            Sprite((x * TILE_SIZE,y * TILE_SIZE), image, (self.all_sprites, self.collision_sprites))

        for obj in tmx_map.get_layer_by_name('Triggers'):
            if obj.name == 'Data':
                self.extract_info(obj)

            if obj.name == 'Camera1':
                self.camera1 = Camera((obj.x, obj.y))
            if obj.name == 'Camera2':
                self.camera2 = Camera((obj.x, obj.y))
            if obj.name == 'Win':
                self.win_rect = pygame.Rect(obj.x, obj.y, obj.width, obj.height)
            if obj.name == 'Unactive':
                self.unactive_rect = pygame.Rect(obj.x, obj.y, obj.width, obj.height)

        
        for obj in tmx_map.get_layer_by_name('Entities'):
            if obj.name == 'Player0':
                self.player0 = Player((obj.x, obj.y), self.player_frames, (self.all_sprites, self.player_sprites, self.game_objects, self.slide_objects), self.collision_sprites, self.battery_sprites, self.tablet_sprites, self.slide_objects, 0) # collision_sprite is not in (groups) causeonly need to check for walls
            if obj.name == 'Player1':
                self.player1 = Player((obj.x, obj.y), self.player_frames, (self.all_sprites, self.player_sprites, self.game_objects, self.slide_objects), self.collision_sprites, self.battery_sprites, self.tablet_sprites, self.slide_objects, 1)
            if obj.name == 'Player2':
                self.player2 = Player((obj.x, obj.y), self.player_frames, (self.all_sprites, self.player_sprites, self.game_objects, self.slide_objects), self.collision_sprites, self.battery_sprites, self.tablet_sprites, self.slide_objects, 2)

    def background(self):
        # create bg
        self.bg = self.cutscene_frames['background']
        self.bg = pygame.transform.scale(self.bg, FULL_SCREEN_SIZE)
        self.bg_rect = self.bg.get_rect(center=self.display_surface.get_rect().center)

    def impact_trigger(self):
        # some time the save misses (when the shake miss too)
        for obj in self.slide_objects:  # does not currently save when obj is 'awakened'
            if obj.old_rect.topleft != obj.rect.topleft and obj.stationnary and (obj.state == 'active' or obj.state == 'awakened'): # obj stop place
                self.audio.play_sfx('impact_a')
                self.screen_shake()

                x, y = obj.rect.topleft
                offset_x = x - FULL_OFFSET_X
                offset_y = y- FULL_OFFSET_Y
                if self.camera == self.camera2: # is full screen
                    if obj.hit == 'up':
                        for i in range(10):
                            self.particle1.add_particles_up(x, y)
                    if obj.hit == 'down':
                        for i in range(10):
                            self.particle1.add_particles_down(x, y)
                    if obj.hit == 'left':
                        for i in range(10):
                            self.particle1.add_particles_left(x, y)
                    if obj.hit == 'right':
                        for i in range(10):
                            self.particle1.add_particles_right(x, y)
                else:
                    if obj.hit == 'up':
                        for i in range(10):
                            #self.particle1.add_particles_up(obj.rect.topleft[0] - FULL_OFFSET_X, obj.rect.topleft[1] - FULL_OFFSET_Y)
                            self.particle1.add_particles_up(offset_x, offset_y)
                    if obj.hit == 'down':
                        for i in range(10):
                            self.particle1.add_particles_down(offset_x, offset_y)
                    if obj.hit == 'left':
                        for i in range(10):
                            self.particle1.add_particles_left(offset_x, offset_y)
                    if obj.hit == 'right':
                        for i in range(10):
                            self.particle1.add_particles_right(offset_x, offset_y)

    def extract_info(self, obj):
        # get the level info with the data icon

        self.bg_color = obj.properties['bg']
        self.level_num = obj.properties['level_number']
        unlock_string = obj.properties['level_unlock']

        parts = unlock_string.split(',')
        self.level_unlock = []
        for part in parts:
            part = part.strip()  # remove spaces
            if part.isdigit():
                self.level_unlock.append(int(part))

    def screen_shake(self):
        if self.save.file_info['shake']:
            for player in self.player_sprites:
                if player.hit == 'up':
                    self.all_sprites.shake_timer_up.activate()
    
                if player.hit == 'down':
                    self.all_sprites.shake_timer_down.activate()
    
                if player.hit == 'left':
                    self.all_sprites.shake_timer_left.activate()
    
                if player.hit == 'right':
                    self.all_sprites.shake_timer_right.activate()

    def particle_event(self):
        for player in self.slide_objects:
            if player.direction != [0, 0]:
                if self.camera == self.camera2: # is full screen
                    self.particle2.add_particles(player.rect.x, player.rect.y, pygame.Color('White'))
                else:
                    self.particle2.add_particles(player.rect.x - FULL_OFFSET_X, player.rect.y - FULL_OFFSET_Y, pygame.Color('White'))

            #if player.state == 'awakened':
            #    if self.camera == self.camera2: # is full screen
            #        self.particle1.add_particles_right(player.x - FULL_OFFSET_X *2, player.y - FULL_OFFSET_Y*2)
            #    else:
            #        self.particle1.add_particles_right(player.x - FULL_OFFSET_X, player.y - FULL_OFFSET_Y)

    def input(self):
        pass

    def timer_setup(self):
        # general timer
        #self.particle_event_timer = Timer(10, self.particle_event, True, True)
        self.cutscene_timer = Timer(5000, autostart = True)

    def timer_management(self):
        if self.cutscene_timer.active:
            #print(self.cutscene_timer.time_passed)
            pass
        else:
            self.switch_level('home', None)

    def run(self, dt):
        self.input()

        # update
        self.all_sprites.update(dt)
        self.impact_trigger()
        self.timer_management()
        
        # draw 
        self.display_surface.blit(self.bg, self.bg_rect)
        self.particle2.emit()
        self.all_sprites.draw(self.camera.pos)
        self.particle1.emit()
        self.particle_event_timer.update()
        self.cutscene_timer.update()


        # debug section

        try:
            debug(f'player flash is {self.player0.flash_flag}', 130)
        #    debug(f'active index  {self.active_player_index}', 30)
        #    debug(f'self.activation_order  {self.activation_order}', 50)
        #    debug(f'self.player0.is_next  {self.player0.is_next}', 70)
        #    debug(f'self.player1.is_next  {self.player1.is_next}', 90)
        #    debug(f'self.player2.is_next {self.player2.is_next}', 110)
        #    
        except:
            pass




