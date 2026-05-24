
from settings import *
from sprites import Sprite
from groups import AllSprites
from sprites import *
from support import * 
from timers import Timer
from camera import Camera   
from debug import *
from particle import ImpactParticle, SlideParticle

#from nebulon import Player, NebulonController


## Level class will contain all the method of the game so far
class Cutscene:
    def __init__(self, tmx_map, save, data, cutscene_frames, audio, switch_level, screen_dimension, ending_num):
        self.display_surface = pygame.display.get_surface()
        self.clock = pygame.time.Clock()
        self.save = save
        self.data = data
        self.audio = audio
        self.switch_level = switch_level
        self.cutscene_frames = cutscene_frames
        self.screen_dimension = screen_dimension
        self.ending_num = ending_num
        self.setup_flag = True

        self.all_sprites = AllSprites()
        self.collision_sprites = pygame.sprite.Group()
        self.slide_objects = pygame.sprite.Group()

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

        # Nebulon Controller for ordered movement
        self.nebulon_controller = None
        self.setup_nebulon_controller()

    def load_assets(self, cutscene_frames):
        self.nebulons = []  # List of nebulons (Player instances)
        self.player_frames = cutscene_frames['player']

    def create_assets(self):
        # create particles
        self.PARTICLE_EVENT = pygame.USEREVENT + 1
        pygame.time.set_timer(self.PARTICLE_EVENT, 10)
        self.particle1 = ImpactParticle((0, 0), self.all_sprites, self.screen_dimension)
        self.particle2 = SlideParticle((0, 0), self.all_sprites, self.screen_dimension)
        self.particle_event_timer = Timer(10, self.particle_event, True, True)

    def setup_nebulon_controller(self):
        # Ensure nebulons are sorted by serial number
        self.nebulons.sort(key=lambda n: n.serial_num)
        self.nebulon_controller = NebulonController(self.nebulons, self.ending_num)

    def setup(self, tmx_map):
        self.level_width = tmx_map.width * TILE_SIZE
        self.level_height = tmx_map.height * TILE_SIZE

        wait_time = 4000

        # make the tile invisible
        for x, y, image in tmx_map.get_layer_by_name('Main').tiles():
            transparent_image = pygame.Surface(image.get_size(), pygame.SRCALPHA)
            transparent_image.fill((0, 0, 0, 0))
            Sprite((x * TILE_SIZE,y * TILE_SIZE), transparent_image, (self.all_sprites, self.collision_sprites))


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

        wait_time = 4200

        # Create nebulons with specific trigger times
        for obj in tmx_map.get_layer_by_name('Entities'):
            if obj.name.isdigit():
                serial_num = int(obj.name)
                trigger_time = wait_time + self.calculate_trigger_offset(serial_num)
                
                self.player = Player(
                    (obj.x, obj.y),
                    self.player_frames,
                    (self.all_sprites, self.slide_objects), #enkever d'all sprites
                    self.collision_sprites,
                    self.slide_objects,
                    serial_num,
                    trigger_time  # Pass trigger_time to Player
                )
                
                # Manually set trigger_time on player
                self.player.trigger_time = trigger_time
                self.nebulons.append(self.player)

    def calculate_trigger_offset(self, serial_num):
        # Calculate the offset based on serial number
        if self.ending_num == 1:
            offsets = {
                0: 0, 1: 0, 2: 2000, 3: 2600, 4: 2700,
                5: 2900, 6: 2700, 7: 3000, 8: 3000,  9: 3100, 
                10: 3200, 11: 3300, 12: 3400, 13: 3500, 14: 3600, 
                15: 3700, 16: 3800, 17: 3900, 18: 4000, 19: 4100,
                20: 4200, 21: 4300, 22: 4400, 23: 4500, 24: 4600, 
                25: 4700, 26: 4800, 27: 4900, 28: 5000, 29: 5000, 
                30: 5200, 31: 5300, 32: 5400, 33: 5500, 34: 5600, 
                35: 5700, 36: 5600, 37: 5900, 38: 6000, 39: 6100, 
                40: 6200, 41: 6300, 42: 6400
            }
        elif self.ending_num == 2:
            offsets = {
                0: 0, 1: 0, 2: 2000, 3: 2600, 4: 2700,
                5: 2900, 6: 2700, 7: 3000, 8: 3000, 9: 3100,
                10: 3200, 11: 3300, 12: 3400, 13: 3500, 14: 3600,
                15: 3700, 16: 3800, 17: 3900, 18: 4000, 19: 4100,
                20: 4200, 21: 4300, 22: 4400, 23: 4500, 24: 4600,
                25: 4700, 26: 4800, 27: 4900, 28: 5000, 29: 5000,
                30: 5200, 31: 5300, 32: 5400, 33: 5500, 34: 5600,
                35: 5700, 36: 5600, 37: 5900, 38: 6000, 39: 6100,
                40: 6200, 41: 6300, 42: 6400, 43: 6500, 44: 6600,
                45: 6700, 46: 6800, 47: 6900, 48: 7000, 49: 7100,
                50: 7200, 51: 7300, 52: 7400, 53: 7500, 54: 7600,
                55: 7700, 56: 7800, 57: 7900, 58: 8000, 59: 8100,
                60: 8200, 61: 8300, 62: 8400, 63: 8500, 64: 8600,
                65: 8700, 66: 8800, 67: 8900, 68: 9000, 69: 9100,
                70: 9200, 71: 9300, 72: 9400, 73: 9500, 74: 9600,
                75: 9700, 76: 9800, 77: 9900, 78: 10000, 79: 10100,
                80: 10200, 81: 10300, 82: 10400, 83: 10500, 84: 10600,
                85: 10700, 86: 10800, 87: 10900, 88: 11000, 89: 11100,
                90: 11200, 91: 11300, 92: 11400, 93: 11500, 94: 11600,
                95: 11700, 96: 11800, 97: 11900, 98: 12000, 99: 12100,
                100: 12200, 101: 12300, 102: 12400, 103: 12500, 104: 12600, 
                105: 12700, 106: 12800, 107: 12900, 108: 13000, 109: 13100, 
                110: 13200, 111: 13300, 112: 13400, 113: 13500, 114: 13600, 
                115: 13700, 116: 13800, 117: 13900, 118: 14000, 119: 14100, 
                120: 14200, 121: 14300, 122: 14400, 123: 14500, 124: 14600
            }

        return offsets.get(serial_num, 0)  # Default to 0 if not listed

    def background(self):
        # create bg
        self.bg = self.cutscene_frames['background']
        self.bg = pygame.transform.scale(self.bg, FULL_SCREEN_SIZE)
        self.bg_rect = self.bg.get_rect(center=self.display_surface.get_rect().center)

    def impact_trigger(self):
        for obj in self.slide_objects:
            if obj.old_rect.topleft != obj.rect.topleft and obj.stationnary and (obj.state == 'active' or obj.state == 'awakened'): # obj stop place
                self.audio.play_sfx('impact_a')

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

    def particle_event(self):
        for nebulon in self.nebulons:
            if nebulon.direction != [0, 0]:
                x, y = nebulon.rect.x, nebulon.rect.y

                self.particle2.add_particles(
                    x + self.all_sprites.offset.x,
                    y + self.all_sprites.offset.y + 64,
                    COLORS['white']
                )

    def timer_setup(self):
        # general timer
        #self.particle_event_timer = Timer(10, self.particle_event, True, True)
        self.cutscene_timer = Timer(19200, autostart = True) #19200

    def timer_management(self):
        if self.cutscene_timer.active:
            debug(self.cutscene_timer.elapsed_time, 50)
        else:
            self.switch_level('home', None)

    def run(self, dt):
        # update
        self.all_sprites.update(dt)
        self.impact_trigger()
        self.timer_management()
        
        # Control the nebulon movement
        if self.nebulon_controller:
            self.nebulon_controller.update(dt)

        # draw 
        self.display_surface.blit(self.bg, self.bg_rect)
        self.particle2.emit()
        self.all_sprites.draw(self.camera.pos)
        
        for nebulon in self.nebulons:
            if nebulon.direction != [0, 0] or self.setup_flag:
                draw_pos = (nebulon.rect.topleft[0] - self.camera.pos[1],
                            nebulon.rect.topleft[1] - self.camera.pos[0])
                self.display_surface.blit(nebulon.image, nebulon.rect.topleft)
        self.particle1.emit()
        self.particle_event_timer.update()
        self.cutscene_timer.update()


class NebulonController:
    def __init__(self, nebulons, ending_num):
        self.nebulons = nebulons
        self.ending_num = ending_num
        self.start_time = pygame.time.get_ticks()  # Record the starting time
        self.current_index = 0

    def move_nebulon(self, nebulon):
        if self.ending_num == 1:
            south_gang = [2, 5, 10, 14, 18, 21, 27, 33, 35]
            north_gang = [3, 7, 8, 9, 12, 16, 20, 25, 29, 31, 38, 40, 42]
            west_gang = [0, 8, 11, 15, 17, 24, 28, 30, 34, 37, 41]
            east_gang = [1, 4, 6, 11, 13, 19, 22, 23, 26, 32, 36, 39]

        elif self.ending_num == 2:
            north_gang = [3, 7, 9, 12, 16, 20, 25, 29, 31, 38, 40, 43, 47, 51, 55, 59, 63, 67, 71, 75, 79, 83, 87, 91, 95, 99, 103, 107, 111, 115, 119, 120]
            east_gang = [1, 4, 6, 11, 13, 19, 22, 23, 26, 32, 36, 39, 44, 48, 52, 56, 60, 64, 68, 72, 76, 80, 84, 88, 92, 96, 100, 104, 108, 112, 116, 121, 124]
            south_gang = [2, 5, 10, 14, 18, 21, 27, 33, 35, 45, 49, 52, 57, 61, 65, 69, 73, 77, 81, 85, 89, 93, 97, 101, 105, 109, 113, 117, 122]
            west_gang = [8, 11, 15, 17, 24, 28, 30, 34, 37, 41, 42, 46, 50, 54, 58, 62, 66, 70, 74, 78, 82, 86, 90, 94, 98, 102, 106, 110, 114, 118, 123]
            

        if nebulon.serial_num in south_gang:
            nebulon.direction.y = -1
        elif nebulon.serial_num in north_gang:
            nebulon.direction.y = 1
        elif nebulon.serial_num in west_gang:
            nebulon.direction.x = 1
        elif nebulon.serial_num in east_gang:
            nebulon.direction.x = -1

        #print(f'nebulon{nebulon.serial_num} moved at {pygame.time.get_ticks()}')

    def update(self, dt):
        current_time = pygame.time.get_ticks() - self.start_time

        # Check if the next nebulon is ready to move
        while self.current_index < len(self.nebulons):
            nebulon = self.nebulons[self.current_index]
            if current_time >= nebulon.trigger_time:
                self.move_nebulon(nebulon)
                self.current_index += 1
            else:
                break  # Wait for the next trigger time

class Player(AnimatedSprite):
    def __init__(self, pos, frames, groups, collision_sprites, slide_objects, serial_num, start_time):
        AnimatedSprite.__init__(self, pos, frames, groups) # Sprite instead of super for now

        self.serial_num = serial_num
        self.start_time = start_time
        self.frames = frames

        # Movement & collision
        self.direction = pygame.Vector2(0, 0)
        self.collision_sprites = collision_sprites
        self.slide_objects = slide_objects
        self.speed = 1800

        self.flash_timer = 0
        self.current_frame = 0

        self.iddle_time = 0

        self.hit = None
        self.stationnary = False
        self.can_slide = False
        self.collision_flag = False
        self.animation = True

        #self.super_inactive = False
        self.old_rect = self.rect.copy()

        # Timers
        self.impact_face = Timer(400)
        self.iddle_face = Timer(4000)
        self.start_timer = Timer(start_time)#, self.auto_move)

        #pass dt
        self.start_timer.use_delta_time = True

        self.start_timer.activate(use_dt = True)

    def animate(self, dt):
        # overwrite the animate method from AnimatedSprite class to account for different player state
        # current logic doesnt use show_x logic but relly on frame count, advantage is that it knows exactly when to stop
        if self.direction != [0, 0]:
            self.impact_face.activate()
        # general animations
        if self.impact_face.active:
            self.current_frame = 8
        else:
            self.current_frame = 2

        self.image = self.frames[self.current_frame]

    def wall_collision(self):
        # there was a bug that desyc collision but should be fixed
        collision_group = [sprite for sprite in self.collision_sprites]  # Exclude self if needed elsewhere
        for sprite in collision_group:
            # Slightly inflate sprite rect to catch edge-touching cases
            sprite_rect = sprite.rect.inflate(-1, -1)

            if sprite_rect.colliderect(self.rect):
                if self.direction.x > 0:  # Moving right
                    if self.rect.right <= sprite.rect.right:  # Within or before the right edge
                        self.hit = 'right'
                        self.rect.right = sprite.rect.left
                        self.direction.x = 0
                        self.stationnary = True

    def object_collision(self, direction): # completely stop the movement if far
        collision_group = [sprite for sprite in self.slide_objects if sprite != self]# exclude itself for collision group (but not other players)
        if collision_group:
            for sprite in collision_group:       
                if sprite.rect.colliderect(self.rect): 
                    self.collision_flag = True
                    if not sprite.can_slide: # collision with every object at a distance (section exactly the same as wall_collision, could be optimised?)
                        if direction == 'horizontal':
                            if self.direction.x != 0:
                                self.hit = 'right' if self.direction.x > 0 else 'left'
                                self.rect.right = sprite.rect.left if self.hit == 'right' else self.rect.right
                                self.rect.left = sprite.rect.right if self.hit == 'left' else self.rect.left

                                self.direction.x = 0
                                self.stationnary = True
                                
                        if direction == 'vertical':
                            if self.direction.y != 0:
                                self.hit = 'down' if self.direction.y > 0 else 'up'
                                self.rect.bottom = sprite.rect.top if self.hit == 'down' else self.rect.bottom
                                self.rect.top = sprite.rect.bottom if self.hit == 'up' else self.rect.top

                                self.direction.y = 0
                                self.stationnary = True

    def move(self, dt):
        # Move horizontally and check for wall collision first
        self.rect.x += self.direction.x * self.speed * dt
        self.rect.y += self.direction.y * self.speed * dt
        self.wall_collision()
        self.object_collision('horizontal')
        self.object_collision('vertical')

    def update(self, dt):
        self.old_rect = self.rect.copy()
        # update only when active to prevent lag
        if self.current_frame != 2 or self.direction != [0,0]:
            self.start_timer.update(dt)
            self.impact_face.update()
            self.iddle_face.update()

            self.animate(dt)
            self.move(dt)
     










        

        
