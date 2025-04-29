from sprites import *
from math import sin, floor


class Player(AnimatedSprite):
    def __init__(self, pos, frames, groups, collision_sprites, battery_sprites, tablet_sprites, slide_objects, serial_num):
        AnimatedSprite.__init__(self, pos, frames, groups) # Sprite instead of super for now

        self.serial_num = serial_num
        self.frames = frames

        # Movement & collision
        self.direction = pygame.Vector2(0, 0)
        self.collision_sprites = collision_sprites
        self.battery_sprites = battery_sprites
        self.tablet_sprites = tablet_sprites
        self.slide_objects = slide_objects
        self.speed = 1800

        self.flash_timer = 0
        self.current_frame = 0

        self.iddle_time = 0

        self.hit = None
        self.stationnary = True
        self.animation = True
        self.slide_finished = False
        self.can_be_shut_off = False
        self.can_slide = False
        self.is_active = False
        self.flash_flag = False
        self.is_next = False
        self.can_move = False

        #self.super_inactive = False

        self.old_rect = self.rect.copy()

        # Timers
        self.move_delay = Timer(100)
        self.push_delay = Timer(300)
        self.impact_face = Timer(400)
        self.dead_face = Timer(400)
        self.iddle_face = Timer(4000)
        self.flash_delay = Timer(100, repeat=True)

    def state_management(self, dt):
        if self.state == 'dead':
            self.rect.x, self.rect.y = DEAD_PLAYER_X, DEAD_PLAYER_Y
        if self.state == 'outside':
            self.rect.x, self.rect.y = OUTSIDE_PLAYER_X, OUTSIDE_PLAYER_Y
        if self.state == 'awakened':
            self.image = self.flash(dt)

    def flash(self, dt):
        self.flash_timer += dt * 2
        if self.flash_timer >= 0.25:
            self.flash_flag = not self.flash_flag
            self.flash_timer = 0

        flash_surf = self.image.copy()
        if self.flash_flag:
            intensity = 25

            # Apply pixel-wise brightening effect using Pygame's blend mode
            overlay = pygame.Surface(self.image.get_size(), pygame.SRCALPHA)
            overlay.fill((intensity, intensity, intensity, 0))  # Only increase RGB, keep alpha the same
            # Use BLEND_RGB_ADD to add to tint
            flash_surf.blit(overlay, (0, 0), special_flags=pygame.BLEND_RGB_ADD)
        return flash_surf

    def input(self):
        keys = pygame.key.get_pressed()
        self.is_active = True
        if self.stationnary and not self.move_delay.active and not self.push_delay.active:
            self.can_move = True
            if keys[pygame.K_d]:
                self.direction.x = 1
                self.stationnary = False  # Disable further direction changes
            elif keys[pygame.K_a]:
                self.direction.x = -1
                self.stationnary = False
            elif keys[pygame.K_w]:
                self.direction.y = -1
                self.stationnary = False
            elif keys[pygame.K_s]:
                self.direction.y = 1
                self.stationnary = False
        else:
            self.can_move = False

    def animate(self, dt):
        # overwrite the animate method from AnimatedSprite class to account for different player state
        # current logic doesnt use show_x logic but relly on frame count, advantage is that it knows exactly when to stop

        wake = False
        iddle = False

        # general animations
        if self.is_active:
            if self.current_frame <= 1:
                wake = True
            if wake == False:
                if self.direction != [0, 0]:
                    self.impact_face.activate()
                if self.impact_face.active:
                    if not self.state == 'awakened':
                        self.current_frame = 9
                    if self.state == 'awakened':
                        self.current_frame = 8
                    if self.dead_face.active:
                        self.current_frame = 10
                else:
                    self.current_frame = 2
        
            if self.push_delay.active and not self.can_slide:
                self.current_frame = 4
        
        # fix: allow wake only for 2 players
        if not self.is_active and self.current_frame >= 1:
            if not self.can_be_shut_off:
                wake = True
        
        # handle shutdown and semi-active for 3+ players
        if self.can_be_shut_off:
            if not self.is_active and not self.is_next:
                wake = False
                self.current_frame = 11
            elif self.is_next:
                wake = False
                self.current_frame = 0  # explicitly show semi-active sprite
        

        # iddle animation
        if self.is_active and self.direction == [0, 0]:
            self.iddle_time += dt
        else: 
            self.iddle_time = 0

        if self.iddle_face.active:
            iddle = True
            self.iddle_time = 0

        if self.iddle_time >= 15:
            self.iddle_face.activate()
            self.iddle_time = 0

        if self.direction != [0, 0] or not self.is_active: # stop iddle when start moving of switch
            self.iddle_face.deactivate()
            iddle = False

        # animation loops
        if wake:
            self.frame_index += self.animation_speed * dt
            self.current_frame = int(self.frame_index) % 4 #len(self.frames)
        if iddle:
            self.frame_index += self.animation_speed * dt / 3
            cycle_index = self.frame_index % 5
            self.current_frame = 5 if cycle_index <= 4 else 6


        self.image = self.frames[self.current_frame]

    def show_active(self): # currently serve no function
        self.get_inactive = False
        self.get_active = True

    def show_inactive(self):
        self.get_active = False
        self.get_inactive = True

    def wall_collision(self, direction):
        if self.state != 'awakened':
            collision_group = [sprite for sprite in self.collision_sprites] # exclude itself for collision group (but not other players)
            for sprite in collision_group:  
                if sprite.rect.colliderect(self.rect):
                    self.move_delay.activate()
                    if direction == 'horizontal':
                        if self.direction.x != 0:
                            self.hit = 'right' if self.direction.x > 0 else 'left'
                            self.rect.right = sprite.rect.left if self.hit == 'right' else self.rect.right
                            self.rect.left = sprite.rect.right if self.hit == 'left' else self.rect.left

                            for obj in self.slide_objects:
                                obj.direction.x = 0
                                obj.stationnary = True


                    if direction == 'vertical':
                        if self.direction.y != 0:
                            self.hit = 'down' if self.direction.y > 0 else 'up'
                            self.rect.bottom = sprite.rect.top if self.hit == 'down' else self.rect.bottom
                            self.rect.top = sprite.rect.bottom if self.hit == 'up' else self.rect.top

                            for obj in self.slide_objects:
                                obj.direction.y = 0
                                obj.stationnary = True

    def object_collision(self, direction): # completely stop the movement if far
        collision_group = [sprite for sprite in self.slide_objects if sprite != self]# exclude itself for collision group (but not other players)
        if collision_group and self.battery_sprites and not self.is_active: # can collide with battery if unactive
            collision_group += list(self.battery_sprites)
            if self.tablet_sprites:
                collision_group += list(self.tablet_sprites)

        if collision_group:
            for sprite in collision_group:       
                if sprite.rect.colliderect(self.rect): 
                    if not sprite.can_slide: # collision with every object at a distance (section exactly the same as wall_collision, could be optimised?)
                        self.move_delay.activate()
                        if direction == 'horizontal':
                            if self.direction.x != 0:
                                self.hit = 'right' if self.direction.x > 0 else 'left'
                                self.rect.right = sprite.rect.left if self.hit == 'right' else self.rect.right
                                self.rect.left = sprite.rect.right if self.hit == 'left' else self.rect.left

                                for obj in self.slide_objects:
                                    obj.direction.x = 0
                                    obj.stationnary = True
                                
                        if direction == 'vertical':
                            if self.direction.y != 0:
                                self.hit = 'down' if self.direction.y > 0 else 'up'
                                self.rect.bottom = sprite.rect.top if self.hit == 'down' else self.rect.bottom
                                self.rect.top = sprite.rect.bottom if self.hit == 'up' else self.rect.top

                                for obj in self.slide_objects:
                                    obj.direction.y = 0
                                    obj.stationnary = True

                    if sprite.can_slide: # the slide trigger each frame
                        self.push_delay.activate() # using the form of the previous collision checks makes it messier 
                        # timer
                        if direction == 'horizontal':
                            if self.direction.x > 0:                               
                                sprite.direction.x = 1
                                self.rect.right = sprite.rect.left
                                self.direction.x = 0
                                sprite.stationnary = False

                            elif self.direction.x < 0:                                
                                sprite.direction.x = -1
                                self.rect.left = sprite.rect.right
                                self.direction.x = 0
                                sprite.stationnary = False

                        if direction == 'vertical':
                            if self.direction.y > 0:
                                sprite.stationnary = False
                                sprite.direction.y = 1
                                self.rect.bottom = sprite.rect.top
                                self.direction.y = 0

                            elif self.direction.y < 0:
                                sprite.stationnary = False
                                sprite.direction.y = -1
                                self.rect.top = sprite.rect.bottom
                                self.direction.y = 0

    def move(self, dt):
        # Move horizontally and check for wall collision first
        self.rect.x += self.direction.x * self.speed * dt
        self.rect.y += self.direction.y * self.speed * dt
        self.wall_collision('horizontal')
        self.wall_collision('vertical')
        self.object_collision('horizontal')
        self.object_collision('vertical')

    def update(self, dt):
        self.old_rect = self.rect.copy()
        self.move_delay.update()
        self.push_delay.update()
        self.flash_delay.update()
        self.impact_face.update()
        self.dead_face.update()
        self.iddle_face.update()
        
        self.animate(dt)
        self.move(dt)
        self.state_management(dt)
        

        





        

        