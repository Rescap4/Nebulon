from settings import *
from sprites import *
from random import randint




class Particle(Sprite):
    def __init__(self, pos, groups, screen_dimension):  # Ensure compatibility with sprite groups
        self.particles = []
        self.display_surface = screen_dimension  # Should be passed from the game class

    def emit(self):
        if self.particles:
            self.delete_particles()
            for particle in self.particles:
                particle[0][0] += particle[2][0]  # Move horizontally
                particle[0][1] += particle[2][1]  # Vertical
                particle[1] -= 0.5  # Shrink the square

                # Draw a square instead of a circle
                side_length = int(particle[1])  # Size of the square
                if side_length > 0:  # Only draw if size is positive
                    pygame.draw.rect(
                        self.display_surface,
                        pygame.Color('White'),
                        (particle[0][0], particle[0][1], side_length, side_length)
                    )

    def add_particles_up(self, offset_x, offset_y):
        pos_x = offset_x + 32
        pos_y = offset_y - 64
        side_length = 15 
        direction_x = randint(-1, 1)
        direction_y = (randint(-1, 0))/2
        particle_square = [[pos_x, pos_y], side_length, [direction_x, direction_y]]
        self.particles.append(particle_square)

    def add_particles_down(self, offset_x, offset_y):
        pos_x = offset_x + 32
        pos_y = offset_y
        side_length = 15 
        direction_x = randint(-1, 1)
        direction_y = (randint(0, 1))/2
        particle_square = [[pos_x, pos_y], side_length, [direction_x, direction_y]]
        self.particles.append(particle_square)

    def add_particles_left(self, offset_x, offset_y):
        pos_x = offset_x
        pos_y = offset_y - 32
        side_length = 15 
        direction_x = (randint(-1, 0))/2
        direction_y = randint(-1, 1)
        particle_square = [[pos_x, pos_y], side_length, [direction_x, direction_y]]
        self.particles.append(particle_square)

    def add_particles_right(self, offset_x, offset_y):
        pos_x = offset_x + 64
        pos_y = offset_y - 32
        side_length = 15 
        direction_x = (randint(0, 1))/2
        direction_y = randint(-1, 1)
        particle_square = [[pos_x, pos_y], side_length, [direction_x, direction_y]]
        self.particles.append(particle_square)

    def delete_particles(self):
        particle_copy = [particle for particle in self.particles if particle[1] > 0] # only copy particle greater than 0
        self.particles = particle_copy




class SlideParticle(Sprite):
    def __init__(self, pos, groups, screen_dimension):
        #super.__init__()
        self.particles = []
        self.size = 8
        self.display_surface = screen_dimension # will need to be the one in the game class

    def emit(self):
        if self.particles:
            self.delete_particles()
            for particle in self.particles:
                particle[0].width -= 0.5
                particle[0].x += 0.25
                particle[0].height -= 0.5     
                particle[0].y += 0.25

                pygame.draw.rect(self.display_surface, particle[1], particle[0]) # draw a rect around the particle

    def add_particles(self, offset_x, offset_y, color):
        pos_x = 32 + offset_x
        pos_y = -32 + offset_y
        particle_rect = pygame.FRect(pos_x - self.size/2, pos_y - self.size/2, self.size, self.size)
        self.particles.append((particle_rect, color))

    def delete_particles(self):
        particle_copy = [particle for particle in self.particles if particle[0].width > 0] # only copy particle greater than 0
        self.particles = particle_copy

### Line version
#class SlideParticle(Sprite):
#    def __init__(self, pos, groups):
#        # super().__init__()
#        self.particles = []
#        self.lines = []  # Stores (start_pos, end_pos, color, lifetime)
#        self.size = 8
#        self.display_surface = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))  # Should be game display surface
#
#        # Store previous position (for line generation)
#        self.prev_x = pos[0]
#        self.prev_y = pos[1]
#
#    def emit(self):
#        if self.lines:
#            self.delete_lines()
#            for line in self.lines:
#                start_pos, end_pos, color, lifetime, max_lifetime = line
#
#                # Shrink the line thickness over time
#                thickness = max(1, int(8 * (lifetime / max_lifetime)))  # Ensures a minimum thickness of 1
#
#                pygame.draw.line(self.display_surface, color, start_pos, end_pos, thickness)
#
#    def add_particles(self, offset_x, offset_y, color):
#        pos_x = 32 + offset_x
#        pos_y = -32 + offset_y
#
#        max_lifetime = 20  # Initial lifetime
#        self.lines.append(((self.prev_x, self.prev_y), (pos_x, pos_y), color, max_lifetime, max_lifetime))
#
#        # Store new previous position
#        self.prev_x = pos_x
#        self.prev_y = pos_y
#
#        # Add a shrinking rectangle (particle)
#        particle_rect = pygame.FRect(pos_x - self.size / 2, pos_y - self.size / 2, self.size, self.size)
#        self.particles.append((particle_rect, color))
#
#    def delete_lines(self):
#        self.lines = [(start, end, color, lifetime - 1, max_lifetime) for start, end, color, lifetime, max_lifetime in self.lines if lifetime > 0]