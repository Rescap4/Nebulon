from sprites import *
import time

class Icon(Sprite):
    def __init__(self, pos, surf, groups, collision_sprites, node_sprites, audio):
        Sprite.__init__(self, pos, surf, groups)

        self.surf = surf
        self.audio = audio
        self.can_slide = False

        self.alarm = 1
        self.can_slide = False

        # Movement & collision
        self.collision_sprites = collision_sprites
        self.node_sprites = node_sprites

        # Movement timing
        self.move_cooldown = 120
        self.last_move_time = pygame.time.get_ticks()


    def input(self):
        current_time = pygame.time.get_ticks()
        keys = pygame.key.get_pressed()

        if current_time - self.last_move_time >= self.move_cooldown:
        # and if collide with level icon
            if keys[pygame.K_d]:
                self.move(64, 0)
            elif keys[pygame.K_a]:
                self.move(-64, 0)
            elif keys[pygame.K_w]:
                self.move(0, -64)
            elif keys[pygame.K_s]:
                self.move(0, 64)

        # Update the position of the icon
        self.pos = pygame.math.Vector2(self.rect.topleft)

    def animate(self):
        pass

    def move(self, dx, dy):
        new_x, new_y = self.rect.x + dx, self.rect.y + dy
        old_pos = self.rect.topleft  # Save previous position

        self.rect.topleft = (new_x, new_y)

        if self.can_slide: #if not self.collision(): #
            self.rect.topleft = old_pos  # Revert movement if collision occurs
        else:
            self.audio.play_sfx('icon_a')
            self.last_move_time = pygame.time.get_ticks()  # Only update if movement was successful

    def collision(self):
        # collide on anything that is not an unlocked level
        return any(node.rect.colliderect(self.rect) for node in self.node_sprites)


