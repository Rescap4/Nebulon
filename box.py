from sprites import *


class Box(Sprite):
    def __init__(self, pos, surf, groups, collision_sprites, spike_sprites, battery_sprites, tablet_sprites, slide_objects):
        Sprite.__init__(self, pos, surf, groups) # Sprite instead of super for now
        self.surf = surf
        
        # Movement & collision
        self.direction = pygame.Vector2(0, 0)  # Start stationary
        self.collision_sprites = collision_sprites
        self.spike_sprites = spike_sprites
        self.battery_sprites = battery_sprites
        self.tablet_sprites = tablet_sprites
        self.slide_objects = slide_objects
        self.speed = 1800
        self.stationnary = True  # Allow direction change initially
        self.hit = None
        self.can_slide = False
        self.slide_finished = False
        self.old_rect = self.rect.copy()

    def state_management(self):
        if self.state == 'outside':
            self.rect.topleft = (DEAD_PLAYER_X, DEAD_PLAYER_Y)

    def wall_collision(self, direction):
        if not self.stationnary:
            collision_group = [sprite for sprite in self.collision_sprites] # exclude itself for collision group (but not other players)
            for sprite in collision_group:  
                if sprite.rect.colliderect(self.rect):
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

    def object_collision(self, direction):
        if not self.stationnary:
            collision_group = [obj for obj in self.slide_objects if obj != self] + [obj for obj in self.spike_sprites] + [obj for obj in self.battery_sprites] + [obj for obj in self.tablet_sprites]
            if collision_group: 
                for sprite in collision_group:       
                    if sprite.rect.colliderect(self.rect):
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
        self.state_management()
        self.move(dt)




        

        