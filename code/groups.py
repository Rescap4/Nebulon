from settings import * 
from timers import Timer
from random import randint

class AllSprites(pygame.sprite.Group):
    def __init__(self):
        super().__init__()
        self.display_surface = pygame.display.get_surface()
        self.offset = pygame.Vector2()
        self.shake_timer_right = Timer(50)
        self.shake_timer_left = Timer(50)
        self.shake_timer_up = Timer(50)
        self.shake_timer_down = Timer(50)

    def add_sprite(self, sprite, z_index=0):
        sprite.z_index = z_index
        self.add(sprite)

    def draw(self, target_pos):
        # Use live surface dimensions so the camera re-centers correctly when the
        # logical size changes between windowed (1408×832) and fullscreen (proportional)
        neutral_x = -(target_pos[0] - self.display_surface.get_width() / 2)
        neutral_y = -(target_pos[1] - self.display_surface.get_height() / 2)

        if self.shake_timer_right.active:
            self.offset.x = neutral_x + 1
        elif self.shake_timer_left.active:
            self.offset.x = neutral_x - 1
        else:
            self.offset.x = neutral_x

        if self.shake_timer_up.active:
            self.offset.y = neutral_y - 1
        elif self.shake_timer_down.active:
            self.offset.y = neutral_y + 1
        else:
            self.offset.y = neutral_y


        sorted_sprites = sorted(self.sprites(), key=lambda s: getattr(s, 'z_index', 0))
        for sprite in sorted_sprites:
            self.display_surface.blit(sprite.image, sprite.rect.topleft + self.offset)

        # Update shake timers
        self.shake_timer_right.update()
        self.shake_timer_left.update()
        self.shake_timer_up.update()
        self.shake_timer_down.update()



