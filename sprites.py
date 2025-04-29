from settings import * 
from timers import Timer    # important



class Sprite(pygame.sprite.Sprite):
    """Base class for all sprites in the game."""
    def __init__(self, pos, surf, groups):
        super().__init__(groups)

        self.state = "active"  # Default state: "active"

        self.image = surf 
        self.rect = self.image.get_frect(topleft = pos)
        #self.old_rect = self.rect.copy()
        self.is_player = False


        self.pos = pygame.math.Vector2(self.rect.topleft)


    def update_state(self, position, state):
        """Update the sprites's position and state."""
        self.rect.topleft = position
        self.state = state


    def handle_keys(self):
        pass  # To be implemented in child classes

    def get_state(self):
        """Returns the current state and position of the sprite."""
        return {
            "position": self.rect.topleft,
            "state": self.state
        }
        
    
class AnimatedSprite(Sprite):
    def __init__(self, pos, frames, groups):
        self.frames, self.frame_index, self.animation_speed = frames, 0, 10 # Lignes étaient inversés initiallement
        super().__init__(pos, self.frames[self.frame_index], groups)

    def animate(self, dt):
        self.frame_index += self.animation_speed * dt
        self.image = self.frames[int(self.frame_index) % len(self.frames)]



# spike or laser will be a tileset layer that will kill the player on collide_alpha impact
