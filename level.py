from settings import *
from sprites import Sprite
from player import Player
from groups import AllSprites
from support import * 
from timers import Timer
from camera import Camera   
from history import History
from debug import *
from battery import Battery
from tablet import Tablet
from spike import Spike
from box import Box
from grid import Grid
from particle import Particle, SlideParticle
from math import hypot

## Level class will contain all the method of the game so far
class Level:
    def __init__(self, tmx_map, save, data, level_frames, audio, switch_level, screen_dimension):
        self.display_surface = pygame.display.get_surface()
        self.clock = pygame.time.Clock()
        self.save = save
        self.data = data
        self.audio = audio
        self.switch_level = switch_level
        self.level_frames = level_frames
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
        self.load_assets(level_frames)
        self.setup(tmx_map)
        self.create_assets()
        self.background()


        # General variables
        self.active_player_index = 0
        self.has_movement = True
        self.box = False # prevent crash when no box around
        self.camera = self.camera1
        self.win_triggered = False
        self.update_flag = True

        # Initialise history
        self.history = History()
        self.history.save_state(self.game_objects.sprites())  # initial save
        
        # Timers
        self.player_die_timer = Timer(100)
        self.end_timer = Timer(1000, self.ending)
        self.outside_timer = Timer(100, self.switch_active_player)

        self.active_player_num = 0

    def load_assets(self, level_frames):
        self.box_surf = level_frames['box']
        self.battery_surf = level_frames['battery']
        self.tablet_surf = level_frames['tablet']
        self.spike_surf = level_frames['spike']
        self.player_frames = level_frames['player']
        
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

        for x, y, image in tmx_map.get_layer_by_name('Exit').tiles():
            Sprite((x * TILE_SIZE,y * TILE_SIZE), image, (self.all_sprites, self.collision_sprites, self.exit_sprites, self.game_objects))

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
            if obj.name == 'Battery':
                self.battery = Battery((obj.x, obj.y), self.battery_surf, (self.all_sprites, self.battery_sprites, self.game_objects))
            if obj.name == 'Tablet':
                self.tablet_check()
                self.tablet = Tablet((obj.x, obj.y), self.tablet_surf, (self.all_sprites, self.tablet_sprites, self.game_objects))

            if obj.name == 'Spike':
                self.spike = Spike((obj.x, obj.y), self.spike_surf, (self.all_sprites, self.spike_sprites))
            if obj.name == 'Box':
                self.box = Box((obj.x, obj.y), self.box_surf, (self.all_sprites, self.box_sprites,self.game_objects, self.slide_objects), self.collision_sprites, self.spike_sprites, self.battery_sprites, self.tablet_sprites, self.slide_objects) #obj.properties['escape']

            self.grid = Grid(1920, 1280, self.all_sprites, self.save)

    def background(self):
        # create bg
        self.bg = self.level_frames[self.bg_color]
        self.bg = pygame.transform.scale(self.bg, FULL_SCREEN_SIZE)
        self.bg_rect = self.bg.get_rect(center=self.display_surface.get_rect().center)

    def undo(self):
        """Reverts all sprites to the previous saved state."""
        if self.update_flag and len(self.history.records) > 1:
            # Remove the latest record
            self.history.records.pop()
            # Load the new last record
            last_record = self.history.get_last_record()
            if last_record:
                if all(player.state != 'dead' for player in self.player_sprites):
                    self.audio.play_sfx('undo_d')
                for obj, saved_state in zip(self.game_objects, last_record["object"]):
                    obj.update_state(saved_state["position"], saved_state["state"])
        else:
            self.audio.play_sfx('error_a')

    def impact_trigger(self):
        # some time the save misses (when the shake miss too)
        for obj in self.slide_objects:  # does not currently save when obj is 'awakened'
            if obj.old_rect.topleft != obj.rect.topleft and obj.stationnary and (obj.state == 'active' or obj.state == 'awakened'): # obj stop place
                self.audio.play_sfx('impact_a')
                self.history.save_state(self.game_objects.sprites())   
                self.screen_shake()
                obj.stationnary = True

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

    def check_player(self):
        self.activation_order = [player.serial_num for player in sorted(self.player_sprites, key=lambda p: p.serial_num) if player.state != 'outside']
        self.player_count = sum(1 for p in self.player_sprites if p.state != 'outside')
        if self.player_count >= 3:
            for player in self.player_sprites:
                if (player.serial_num - 1) % len(self.player_sprites) == self.active_player_index:
                    player.is_next = True
                else:
                    player.is_next = False
                player.animation = False
                player.can_be_shut_off = True
        else:
            for player in self.player_sprites:
                player.animation = True
                player.can_be_shut_off = False

    def switch_active_player(self):
        if len(self.player_sprites) >= 2:
            self.check_movement()
            if not self.has_movement and self.activation_order:
                # switch sound removed because ennoying
                if self.active_player_index in self.activation_order:
                    current_index = self.activation_order.index(self.active_player_index)
                else:
                    current_index = -1
                self.active_player_index = self.activation_order[(current_index + 1) % len(self.activation_order)]
            else:
                self.audio.play_sfx('error_a')
        else:
            self.audio.play_sfx('error_a')

    def check_movement(self):
        no_move = all(player.direction == [0, 0] for player in self.player_sprites)
        if self.box and no_move:
            no_move = all(box.direction == [0, 0] for box in self.box_sprites)
    
        if no_move and self.update_flag:
            self.has_movement = False
        else:
            self.has_movement = True  # Don't switch players when moving
            
        #print(self.has_movement) sert a rien

    def move_active(self):
        if self.update_flag: # only allow to move when menu closed
            for player in self.player_sprites:
                if player.serial_num == self.active_player_index:
                    player.is_active = True
                    player.input() # activate the active player
                    self.active_player_num = player.serial_num
                else:
                    player.is_active = False

    def spike_collision(self):
        for player in self.player_sprites:
            self.hit_spike = pygame.sprite.spritecollide(player, self.spike_sprites, False) # ,pygame.sprite.collide_mask) à été enlever car bug depuis que mask utilisé depuis player flash
            if self.hit_spike:
                self.audio.play_sfx('die_a')
                player.state = 'dead'
                self.history.save_state(self.game_objects.sprites()) # saves
                self.player_die_timer.activate()
                player.dead_face.activate()


            if player.state == 'dead' and not self.player_die_timer.active:
                self.undo()
       
    def collect_battery(self):
        # checks the collected batteries
        if self.battery_sprites:
            for player in self.player_sprites:
                battery_collected = pygame.sprite.spritecollide(player, self.battery_sprites, False)
                if battery_collected and player.is_active:
                    self.audio.play_sfx('battery_a')
                    for self.battery in battery_collected:
                        # Teleport the specific battery that was collected
                        self.battery.rect.x, self.battery.rect.y = DESTROYED_X, DESTROYED_Y
                        self.battery.state = 'collected'

                    self.all_collected = all(self.battery.state == 'collected' for self.battery in self.battery_sprites)
                    if self.all_collected: #trigger only once since there are no batteries after
                        player.state = 'awakened' # only the one who collects the last battery gets awakened
                        player.flash_delay.activate() # activate flash

                # Add the detroyed blocs to the History
                if player.state == 'awakened': # need to generalise it for 2 player
                    self.audio.play_loop('awakened_e')
                    for exit in self.exit_sprites:  #collision_sprite only with ground tiles might need to change
                        if exit.rect.colliderect(player): #or exit.rect.colliderect(self.player1.rect):
                            self.audio.play_sfx('destroy_d')
                            exit.rect.topleft = (DESTROYED_X, DESTROYED_Y)

                elif player.state != 'awakened' and player.flash_delay.active: # turn off flash when no longer awakened
                    player.flash_delay.deactivate()
                    self.audio.stop_loop()
                else:
                    self.audio.stop_loop()

    def collect_tablet(self):
        if self.tablet_sprites:
            if not self.save.info.get(f'tablet_{self.level_num}') is True:
            # collecting
                for player in self.player_sprites:
                    tablet_collected = pygame.sprite.spritecollide(player, self.tablet_sprites, False)
                    if tablet_collected and player.is_active:
                        self.audio.play_sfx('tablet_b')
                        for self.tablet in tablet_collected:
                            # Teleport the specific tablet that was collected
                            self.tablet.rect.x, self.tablet.rect.y = DESTROYED_X, DESTROYED_Y
                            self.tablet.state = 'collected'

    def tablet_check(self):
        if self.save.file_info.get(f'tablet_{self.level_num}', False):
            ghost_surf = self.tablet_surf.copy()

            grayscale_overlay = pygame.Surface(self.tablet_surf.get_size(), pygame.SRCALPHA)
            grayscale_overlay.fill((0, 0, 0, 255))  # Black, but used with special flag
            ghost_surf.blit(grayscale_overlay, (0, 0), special_flags=pygame.BLEND_RGB_MULT)

            white_overlay = pygame.Surface(self.tablet_surf.get_size(), pygame.SRCALPHA)
            white_overlay.fill((255, 255, 255, 255))
            ghost_surf.blit(white_overlay, (0, 0), special_flags=pygame.BLEND_RGB_ADD)
            ghost_surf.set_alpha(50)

            self.tablet_surf = ghost_surf

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

    def win_square(self):   
        for player in self.player_sprites:
            if not player.rect.colliderect(self.win_rect):
                if not player.rect.colliderect(self.unactive_rect) and player.state != 'outside':
                    self.audio.play_sfx('outside_a')
                    player.state = 'outside' #  when player is outside it teleports (and lose control)
                    self.outside_timer.activate()
                    self.history.save_state(self.game_objects.sprites())

        if self.box_sprites:
            #only check for boxes marked
            for box in self.box_sprites:
                if not box.rect.colliderect(self.win_rect):
                    if not box.rect.colliderect(self.unactive_rect) and box.state != 'outside':
                        box.state = 'outside'
                        self.history.save_state(self.game_objects.sprites())

        if not self.win_triggered and all(player.state == 'outside' for player in self.player_sprites):
            self.win_triggered = True
            if self.tablet_sprites:
                if self.tablet.state == 'collected':
                    print('tablet collected') # the tablet of this level has been collected (trigger déja juste quand collecte la vrai)
                    # do a 'Tablette collectée!!' animation
                    self.save.file_info[f'tablet_{self.level_num}'] = True # will need to adjust the battery num to the corresponding level
            #self.win_particles
            self.audio.play_sfx('win_a')

            # save the level as beem beaten
            self.save.file_info[f'level_{self.level_num}'] = True
            if self.level_num == 51:
                self.outside_timer.deactivate()
                self.end_timer.activate()
                self.audio.stop_loop()
                #self.audio.mute_music()
                
                #self.audio.mute_looped()
            else:
                # unlock level only when not already unlocked
                for i in range(len(self.level_unlock)):
                    key = f'level_{self.level_unlock[i]}'
                    if key not in self.save.file_info:
                        self.save.file_info[key] = False

                self.switch_level('overworld', self.level_unlock) # last parameter will be to unlock new levels
                #self.win_animation()

    def ending(self):
        # will need to fade out black in another function
        self.switch_level('cutscene', None)

    def activate_grid(self):
        self.audio.play_sfx('select_a')
        self.save.file_info['grid'] = not self.save.file_info['grid']

    def activate_shake(self):
        self.audio.play_sfx('select_a')
        self.save.file_info['shake'] = not self.save.file_info['shake']

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

    def slide_distance(self):
        for player in self.player_sprites:
            if player.is_active:
                was_near = any(
                    hypot(player.old_rect.centerx - obj.old_rect.centerx, player.old_rect.centery - obj.old_rect.centery) <= 64
                    for obj in self.slide_objects if obj != player
                )
                is_near = any(
                    hypot(player.rect.centerx - obj.rect.centerx, player.rect.centery - obj.rect.centery) <= 64
                    for obj in self.slide_objects if obj != player
                )
                player.can_slide = was_near and is_near

                for obj in self.slide_objects:
                    if obj != player:
                        obj_was_near = hypot(player.old_rect.centerx - obj.old_rect.centerx, player.old_rect.centery - obj.old_rect.centery) <= 64
                        obj_is_near = hypot(player.rect.centerx - obj.rect.centerx, player.rect.centery - obj.rect.centery) <= 64
                        obj.can_slide = obj_was_near and obj_is_near
   
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
        keys = pygame.key.get_just_pressed()
        if keys[pygame.K_i]:
            self.switch_active_player()  
        if keys[pygame.K_u]:
            self.undo()
        if keys[pygame.K_g]:
            self.activate_grid()
        if keys[pygame.K_t]:
            self.activate_shake()
        if keys[pygame.K_m]: #temporary
            self.history.save_state(self.game_objects.sprites())

    def run(self, dt):
        self.input()

        # update
        self.all_sprites.update(dt)
        self.check_player()
        self.impact_trigger()
        self.move_active()
        self.spike_collision()
        self.collect_battery()
        self.collect_tablet()
        self.win_square()
        self.slide_distance()
        self.check_movement()
        
        # draw 
        self.display_surface.blit(self.bg, self.bg_rect)

        self.particle2.emit()
        self.all_sprites.draw(self.camera.pos)
        self.particle1.emit()
        self.grid.draw(self.display_surface, self.all_sprites.offset)
        self.player_die_timer.update()
        self.outside_timer.update()
        self.particle_event_timer.update()
        self.end_timer.update()


        # debug section

        #try:
        #    debug(f'player flash is {self.player0.flash_flag}', 130)
        #    debug(f'active index  {self.active_player_index}', 30)
        #    debug(f'self.activation_order  {self.activation_order}', 50)
        #    debug(f'self.player0.is_next  {self.player0.is_next}', 70)
        #    debug(f'self.player1.is_next  {self.player1.is_next}', 90)
        #    debug(f'self.player2.is_next {self.player2.is_next}', 110)
        #    
        #except:
        #    pass




