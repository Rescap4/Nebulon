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

    def draw(self, target_pos):
        # Apply shake effect if active
        # Else draw with camera in center
        # Shake x must be higher to perceive it
        
        # shake left?
        if self.shake_timer_right.active:
            shake_right = 1
            self.offset.x = -(target_pos[0] - WINDOW_WIDTH / 2) + shake_right

        elif self.shake_timer_left.active:
            shake_left = -1
            self.offset.x = -(target_pos[0] - WINDOW_WIDTH / 2) + shake_left


        elif self.shake_timer_up.active:
            shake_up = -1
            self.offset.y = -(target_pos[1] - WINDOW_HEIGHT / 2) + shake_up

        elif self.shake_timer_down.active:
            shake_down = 1
            self.offset.y = -(target_pos[1] - WINDOW_HEIGHT / 2) + shake_down

        else:
            self.offset.x = -(target_pos[0] - WINDOW_WIDTH / 2)
            self.offset.y = -(target_pos[1] - WINDOW_HEIGHT / 2)

        for sprite in self:
            self.display_surface.blit(sprite.image, sprite.rect.topleft + self.offset)

        self.shake_timer_right.update()
        self.shake_timer_left.update()
        self.shake_timer_up.update()
        self.shake_timer_down.update()


