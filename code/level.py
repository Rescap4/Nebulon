from settings import *
from sprites import Sprite
from player import Player
from groups import AllSprites
from support import * 
from timers import Timer
from camera import Camera   
from history import History
from debug import *
from battery import Battery, Behind
from tablet import Tablet
from spike import Spike
from box import Box
from grid import Grid
from particle import *
from math import hypot

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
        self.battery_sprites = pygame.sprite.Group()
        self.tablet_sprites = pygame.sprite.Group()
        self.all_sprites = AllSprites()

        self.collision_sprites = pygame.sprite.Group()
        self.player_sprites = pygame.sprite.Group()
        self.spike_sprites = pygame.sprite.Group()
        self.box_sprites = pygame.sprite.Group()
        self.exit_sprites = pygame.sprite.Group()
        self.game_objects = pygame.sprite.Group()
        self.slide_objects = pygame.sprite.Group()

        # load level   
        self.load_assets(level_frames)
        self.setup(tmx_map)
        self.create_assets()
        self.background()


        # General variables
        self.camera = self.camera1
        self.win_triggered = False
        self.box = False
        self.has_movement = True
        self.update_flag = True
        self.active_player_index = 0
        self.active_player_num = 0
        self.cutscene_index = 0

        # Initialise history
        self.history = History()
        self.history.save_state(self.game_objects.sprites())
        
        # Timers
        self.player_die_timer = Timer(200)
        self.end_timer = Timer(2600, self.ending)
        self.outside_timer = Timer(100, self.switch_active_player)
        self.win_timer = Timer(800, self.return_overworld)
    
    def load_assets(self, level_frames):
        self.box_surf = level_frames['box']
        self.battery_surf = level_frames['battery']
        self.behind_surf = level_frames['behind']
        self.tablet_surf = level_frames['tablet']
        self.spike_surf = level_frames['spike']
        self.player_frames = level_frames['player']
        
    def create_assets(self):
        # create particles
        self.PARTICLE_EVENT = pygame.USEREVENT + 1
        pygame.time.set_timer(self.PARTICLE_EVENT, 10)
        self.impact_particle = ImpactParticle((0, 0), self.all_sprites, self.screen_dimension)
        self.slide_particle = SlideParticle((0, 0), self.all_sprites, self.screen_dimension)
        self.destroy_particle = DestroyParticle((0,0), self.all_sprites, self.screen_dimension)
        self.explosion_particle = ExplosionParticle((0,0), self.all_sprites, self.screen_dimension)
        self.battery_particle = BatteryParticle((0,0), self.all_sprites, self.screen_dimension)
        self.awakened_particle = AwakenedParticle((0,0), self.all_sprites, self.screen_dimension)
        self.win_particle = WinParticle((0,0), self.all_sprites, self.screen_dimension)
        
        self.particle_event_timer = Timer(10, self.particle_event, True, True)

        
        # assign destroy colors
        if self.bg_color == 'pink':
            self.destroy_particle.color_options = [pygame.Color('#93388f'), pygame.Color('#f5555d')]
        elif self.bg_color == 'green':
            self.destroy_particle.color_options = [pygame.Color('#5ac54f'), pygame.Color('#99e65f')]
        elif self.bg_color == 'orange':
            self.destroy_particle.color_options = [pygame.Color('#ed7614'), pygame.Color('#ffc825')]
        elif self.bg_color == 'blue':
            self.destroy_particle.color_options = [pygame.Color('#4B5BAB'), pygame.Color('#00cdf9')]
        elif self.bg_color == 'black':
            self.destroy_particle.color_options = [pygame.Color('#323E4F'), pygame.Color('#7E7E8F')]      

        # assign destroy colors
        if self.bg_color == 'pink':
            self.win_particle.color_options = [pygame.Color('#93388f'), pygame.Color('#f5555d')]
        elif self.bg_color == 'green':
            self.win_particle.color_options = [pygame.Color('#5ac54f'), pygame.Color('#99e65f')]
        elif self.bg_color == 'orange':
            self.win_particle.color_options = [pygame.Color('#ed7614'), pygame.Color('#ffc825')]
        elif self.bg_color == 'blue':
            self.win_particle.color_options = [pygame.Color('#4B5BAB'), pygame.Color('#00cdf9')]
        elif self.bg_color == 'black':
            self.win_particle.color_options = [pygame.Color('#323E4F'), pygame.Color('#7E7E8F')]    

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
                self.all_sprites.add_sprite(self.player0, z_index=1)
            if obj.name == 'Player1':
                self.player1 = Player((obj.x, obj.y), self.player_frames, (self.all_sprites, self.player_sprites, self.game_objects, self.slide_objects), self.collision_sprites, self.battery_sprites, self.tablet_sprites, self.slide_objects, 1)
                self.all_sprites.add_sprite(self.player1, z_index=1)
            if obj.name == 'Player2':
                self.player2 = Player((obj.x, obj.y), self.player_frames, (self.all_sprites, self.player_sprites, self.game_objects, self.slide_objects), self.collision_sprites, self.battery_sprites, self.tablet_sprites, self.slide_objects, 2)
                self.all_sprites.add_sprite(self.player2, z_index=1)
            if obj.name == 'Battery':
                self.behind = Behind((obj.x, obj.y), self.behind_surf, self.all_sprites)
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
        else: #not self.update_flag and len(self.history.records) > 1 and self.update_flag:
            self.audio.play_sfx('error_a')

    def impact_trigger(self):
        for obj in self.slide_objects:
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
                            self.impact_particle.add_particles_up(x, y)
                    if obj.hit == 'down':
                        for i in range(10):
                            self.impact_particle.add_particles_down(x, y)
                    if obj.hit == 'left':
                        for i in range(10):
                            self.impact_particle.add_particles_left(x, y)
                    if obj.hit == 'right':
                        for i in range(10):
                            self.impact_particle.add_particles_right(x, y)
                else:
                    if obj.hit == 'up':
                        for i in range(10):
                            #self.impact_particle.add_particles_up(obj.rect.topleft[0] - FULL_OFFSET_X, obj.rect.topleft[1] - FULL_OFFSET_Y)
                            self.impact_particle.add_particles_up(offset_x, offset_y)
                    if obj.hit == 'down':
                        for i in range(10):
                            self.impact_particle.add_particles_down(offset_x, offset_y)
                    if obj.hit == 'left':
                        for i in range(10):
                            self.impact_particle.add_particles_left(offset_x, offset_y)
                    if obj.hit == 'right':
                        for i in range(10):
                            self.impact_particle.add_particles_right(offset_x, offset_y)

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
                self.audio.play_sfx('die_d')
                player.state = 'dead'
                self.history.save_state(self.game_objects.sprites()) # saves
                self.player_die_timer.activate()
                player.dead_face.activate()

                # explosion
                if self.camera == self.camera2: # is full screen
                    self.explosion_particle.add_particles(player.rect.x + 32, player.rect.y - 32)
                else:
                    self.explosion_particle.add_particles(player.rect.x - FULL_OFFSET_X + 32, player.rect.y - FULL_OFFSET_Y - 32)


            if player.state == 'dead' and not self.player_die_timer.active:
                self.undo()
       
    def collect_battery(self):
        # checks the collected batteries
        if self.battery_sprites:
            for player in self.player_sprites:
                battery_collected = pygame.sprite.spritecollide(player, self.battery_sprites, False)
                if battery_collected and player.is_active:
                    
                    for battery in battery_collected:
                        if self.camera == self.camera2: # is full screen
                            self.battery_particle.start_sequence((battery.rect.x + 32, battery.rect.y - 32))
                        else:
                            self.battery_particle.start_sequence((battery.rect.x - FULL_OFFSET_X + 32, battery.rect.y - FULL_OFFSET_Y - 32))

                        # Teleport the specific battery that was collected
                        battery.rect.x, battery.rect.y = DESTROYED_X, DESTROYED_Y
                        battery.state = 'collected'

                    all_collected = all(self.battery.state == 'collected' for self.battery in self.battery_sprites)
                    if all_collected: #trigger only once since there are no batteries after
                        player.state = 'awakened' # only the one who collects the last battery gets awakened
                        player.flash_delay.activate() # activate flash
                        self.audio.play_sfx('battery_a') # could play a sfx for last battery
                    else:
                        self.audio.play_sfx('battery_a')



                # Add the detroyed blocs to the History
                if player.state == 'awakened': # need to generalise it for 2 player
                    for exit in self.exit_sprites:
                        if exit.rect.colliderect(player):
                            # explosion particle
                            if self.camera == self.camera2: # is full screen
                                self.destroy_particle.add_particles(exit.rect.x + 32, exit.rect.y - 32)
                            else:
                                self.destroy_particle.add_particles(exit.rect.x - FULL_OFFSET_X + 32, exit.rect.y - FULL_OFFSET_Y - 32)

                            player.slowed_flag = True
                            player.old_pos = (player.rect.x, player.rect.y)
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
                    self.save.file_info[f'tablet_{self.level_num}'] = True # will need to adjust the battery num to the corresponding level
            #self.win_particles
            self.audio.play_sfx('win_a')

            # save the level as beem beaten
            self.save.file_info[f'level_{self.level_num}'] = True
            # unlock level only when not already unlocked
            for i in range(len(self.level_unlock)):
                key = f'level_{self.level_unlock[i]}'
                if key not in self.save.file_info:
                    self.save.file_info[key] = False
                    
            #save on the .txt file
            self.save.save_to_disk()
                    
            # win state stop update of player
            self.outside_timer.deactivate()
            self.audio.stop_music()   
            if self.level_num in [0, 70]:
                self.end_timer.activate()
                if self.level_num == 70:
                    self.cutscene_index = 1
                else:
                    self.cutscene_index = 2
            else:
                self.win_animation()
                #self.switch_level('overworld', self.level_unlock) # last parameter will be to unlock new levels



                #self.win_animation()
    def win_animation(self):
        self.win_timer.activate()
        # currently create an explosion for every object on screen once this function is called
        #for obj in self.all_sprites:
        #    # explosion particle
        #    if self.camera == self.camera2: # is full screen
        #        self.destroy_particle.add_particles(obj.rect.x + 32, obj.rect.y - 32)
        #    else:
        #        self.destroy_particle.add_particles(obj.rect.x - FULL_OFFSET_X + 32, obj.rect.y - FULL_OFFSET_Y - 32)

        #    self.audio.play_sfx('destroy_d')
        #    obj.rect.topleft = (DESTROYED_X, DESTROYED_Y)
        # if press any button, end the timer so return ealry (but will need to be checked every frame)

        # animation with particle effect

    def return_overworld(self):
        self.switch_level('overworld', self.level_unlock)

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
                    self.slide_particle.add_particles(player.rect.x, player.rect.y, pygame.Color('White'))
                else:
                    self.slide_particle.add_particles(player.rect.x - FULL_OFFSET_X, player.rect.y - FULL_OFFSET_Y, pygame.Color('White'))

            if player.state == 'awakened':
                if self.camera == self.camera2: # is full screen
                    self.awakened_particle.add_particles(player.rect.x, player.rect.y, pygame.Color('White'))
                else:
                    self.awakened_particle.add_particles(player.rect.x - FULL_OFFSET_X, player.rect.y - FULL_OFFSET_Y, pygame.Color('White'))

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

        self.slide_particle.emit()
        self.awakened_particle.emit()
        self.all_sprites.draw(self.camera.pos)
        self.impact_particle.emit()
        self.battery_particle.emit()
        self.destroy_particle.emit()
        self.explosion_particle.emit()
        self.win_particle.emit()

        self.grid.draw(self.display_surface, self.all_sprites.offset)
        
        self.player_die_timer.update()
        self.outside_timer.update()
        self.particle_event_timer.update()
        self.end_timer.update()
        self.win_timer.update()


        # debug section
        #try:
        #    debug(f'player speed is {self.player0.speed}', 30)
        #    
        #except:
        #    pass




