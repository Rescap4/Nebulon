from settings import *
from sprites import *
from random import randint, choice, uniform
from math import pi, cos, sin

class ImpactParticle(Sprite):
    # particle for collision with the ground
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
    # trail particle
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

class DestroyParticle(Sprite):
    def __init__(self, pos, groups, screen_dimension):
        #super().__init__(groups)
        self.particles = []
        self.display_surface = screen_dimension

        # Customizable attributes
        self.size_range = (6, 16)
        self.color_options = [pygame.Color('white')] # default color
        self.particle_count = 12

    def emit(self):
        if self.particles:
            self.delete_particles()
            for rect, color, velocity in self.particles:
                # Move and shrink particle
                rect.x += velocity[0]
                rect.y += velocity[1]
                rect.width -= 0.3
                rect.height -= 0.3

                # Only draw if visible
                if rect.width > 0 and rect.height > 0:
                    pygame.draw.rect(self.display_surface, color, rect)

    def add_particles(self, center_x, center_y):
        for _ in range(self.particle_count):
            size = randint(*self.size_range)
            half = size / 2
            rect = pygame.FRect(center_x - half, center_y - half, size, size)

            velocity = [
                randint(-30, 30) / 10,
                randint(-30, 30) / 10
            ]
            color = choice(self.color_options)

            self.particles.append([rect, color, velocity])

    def delete_particles(self):
        self.particles = [p for p in self.particles if p[0].width > 0 and p[0].height > 0]

class ExplosionParticle(Sprite):
    def __init__(self, pos, groups, screen_dimension):
        self.display_surface = screen_dimension

        self.active = False
        self.center = (0, 0)

        # Shockwave config
        self.max_size = 64
        self.growth_speed = 5
        self.thickness = 3
        self.total_waves = 3
        self.delay = 100  # ms between waves

        # Internal state
        self.waves = []  # List of [size]
        self.last_emit_time = 0
        self.waves_emitted = 0

    def add_particles(self, center_x, center_y):
        self.center = (center_x, center_y)
        self.waves.clear()
        self.waves_emitted = 0
        self.last_emit_time = pygame.time.get_ticks() - self.delay  # force first one instantly
        self.active = True

    def emit(self):
        if not self.active:
            return

        now = pygame.time.get_ticks()

        # Emit new wave
        if self.waves_emitted < self.total_waves and now - self.last_emit_time >= self.delay:
            self.waves.append(0)  # new wave with size 0
            self.waves_emitted += 1
            self.last_emit_time = now

        # Expand & draw each wave
        updated_waves = []
        for size in self.waves:
            size += self.growth_speed
            if size < self.max_size:
                updated_waves.append(size)
                half = size / 2
                rect = pygame.Rect(
                    self.center[0] - half,
                    self.center[1] - half,
                    size,
                    size
                )
                pygame.draw.rect(self.display_surface, pygame.Color('white'), rect, self.thickness)

        self.waves = updated_waves

        # Deactivate when all waves are done
        if self.waves_emitted >= self.total_waves and not self.waves:
            self.active = False

class BatteryParticle(Sprite):
    def __init__(self, pos, groups, screen_dimension):
        self.display_surface = screen_dimension
        self.bursts = []  # List of [rect, velocity, color]
        self.color = pygame.Color('gold')
        self.particle_size = 10
        self.shrink_speed = 0.5
        self.particle_speed = 2

        # Sequence control
        self.burst_delay = 150  # milliseconds between bursts
        self.total_bursts = 1
        self.bursts_emitted = 0
        self.last_emit_time = pygame.time.get_ticks()
        self.center = (0, 0)  # placeholder

        self.active = False

    def start_sequence(self, center):
        self.center_x, self.center_y = center[0], center[1]
        self.bursts_emitted = 0
        self.last_emit_time = pygame.time.get_ticks() - self.burst_delay  # emit immediately
        self.active = True

    def emit(self):
        if self.active:
            now = pygame.time.get_ticks()

            # Update the emission center every frame
            

            # Emit new burst if enough time has passed
            if self.bursts_emitted < self.total_bursts and now - self.last_emit_time >= self.burst_delay:
                self.add_particles(self.center_x, self.center_y)
                self.bursts_emitted += 1
                self.last_emit_time = now

            # Update and draw particles
            self.update_particles()

            # Stop emitting if done
            if self.bursts_emitted >= self.total_bursts and not self.bursts:
                self.active = False


    def add_particles(self, center_x, center_y):
        directions = [
            ( 0, -1), ( 1, -1), ( 1,  0), ( 1,  1),
            ( 0,  1), (-1,  1), (-1,  0), (-1, -1)
        ]
        for dx, dy in directions:
            size = self.particle_size
            half = size / 2
            rect = pygame.FRect(center_x - half, center_y - half, size, size)
            velocity = [dx * self.particle_speed, dy * self.particle_speed]
            self.bursts.append([rect, velocity, self.color])

    def update_particles(self):
        self.bursts = [p for p in self.bursts if p[0].width > 0 and p[0].height > 0]
        for rect, velocity, color in self.bursts:
            rect.x += velocity[0]
            rect.y += velocity[1]
            rect.width -= self.shrink_speed
            rect.height -= self.shrink_speed
            if rect.width > 0 and rect.height > 0:
                pygame.draw.rect(self.display_surface, color, rect)

class AwakenedParticle(Sprite):
    def __init__(self, pos, groups, screen_dimension):
        self.particles = []  # Each particle: [rect, color, lifetime, velocity]
        self.size = 7
        self.display_surface = screen_dimension  # Reference to main screen

    def emit(self):
        if self.particles:
            self.delete_particles()
            for particle in self.particles:
                rect, color, lifetime, velocity = particle

                # Move particle
                rect.x += velocity[0]
                rect.y += velocity[1]

                # Shrink size
                rect.width -= 0.2
                rect.height -= 0.2

                # Fade lifetime
                lifetime -= 1

                pygame.draw.rect(self.display_surface, color, rect)

                # Update particle values
                particle[2] = lifetime
                particle[0] = rect

    def add_particles(self, offset_x, offset_y, color):
        pos_x = 32 + offset_x + uniform(-5, 5)
        pos_y = -32 + offset_y + uniform(-5, 5)
        rect = pygame.FRect(pos_x - self.size / 2, pos_y - self.size / 2, self.size, self.size)
        lifetime = 60

        # Random velocity in x and y (adjust range for spread)
        vx = uniform(-1.5, 1.5)
        vy = uniform(-1.5, 1.5)

        self.particles.append([rect, color, lifetime, (vx, vy)])

    def delete_particles(self):
        # Remove particles that are too small or expired
        self.particles = [p for p in self.particles if p[0].width > 0 and p[2] > 0]

class LastParticle(Sprite):
    def __init__(self, pos, groups, screen_dimension):
        self.display_surface = screen_dimension
        self.bursts = []  # List of [rect, velocity, color, lifetime]
        self.colors = [pygame.Color('white'), pygame.Color('gold'), pygame.Color('yellow')]
        self.particle_size = 12
        self.shrink_speed = 0.6
        self.particle_speed = 3

        # Sequence control
        self.burst_delay = 100  # milliseconds between bursts
        self.total_bursts = 3
        self.bursts_emitted = 0
        self.last_emit_time = pygame.time.get_ticks()
        self.center = (0, 0)
        self.active = False

    def start_sequence(self, center):
        self.center_x, self.center_y = center
        self.bursts_emitted = 0
        self.last_emit_time = pygame.time.get_ticks() - self.burst_delay
        self.active = True

    def emit(self):
        if self.active:
            now = pygame.time.get_ticks()

            if self.bursts_emitted < self.total_bursts and now - self.last_emit_time >= self.burst_delay:
                self.add_particles(self.center_x, self.center_y)
                self.bursts_emitted += 1
                self.last_emit_time = now

            self.update_particles()

            if self.bursts_emitted >= self.total_bursts and not self.bursts:
                self.active = False

    def add_particles(self, center_x, center_y):
        directions = []
        for angle in range(0, 360, 22):  # 16 directions
            rad = angle * (3.14159 / 180)
            dx = round(self.particle_speed * cos(rad), 2)
            dy = round(self.particle_speed * sin(rad), 2)
            directions.append((dx, dy))

        for dx, dy in directions:
            size = randint(self.particle_size - 2, self.particle_size + 4)
            half = size / 2
            rect = pygame.FRect(center_x - half, center_y - half, size, size)
            velocity = [dx, dy]
            color = choice(self.colors)
            lifetime = 30  # frames
            self.bursts.append([rect, velocity, color, lifetime])

    def update_particles(self):
        updated_bursts = []
        for rect, velocity, color, lifetime in self.bursts:
            rect.x += velocity[0]
            rect.y += velocity[1]
            rect.width -= self.shrink_speed
            rect.height -= self.shrink_speed
            lifetime -= 1

            if rect.width > 0 and rect.height > 0 and lifetime > 0:
                pygame.draw.rect(self.display_surface, color, rect)
                updated_bursts.append([rect, velocity, color, lifetime])

        self.bursts = updated_bursts

class WinParticle(Sprite):
    def __init__(self, pos, groups, screen_dimension):
        self.display_surface = screen_dimension

        self.active = False
        self.center = (0, 0)

        # Shockwave config
        self.max_size = 64
        self.growth_speed = 5
        self.thickness = 3
        self.total_waves = 3
        self.delay = 100  # ms between waves

        # Internal state
        self.waves = []  # List of [size]
        self.last_emit_time = 0
        self.waves_emitted = 0

    def add_particles(self, center_x, center_y):
        self.center = (center_x, center_y)
        self.waves.clear()
        self.waves_emitted = 0
        self.last_emit_time = pygame.time.get_ticks() - self.delay  # force first one instantly
        self.active = True

    def emit(self):
        if not self.active:
            return

        now = pygame.time.get_ticks()

        # Emit new wave
        if self.waves_emitted < self.total_waves and now - self.last_emit_time >= self.delay:
            self.waves.append(0)  # new wave with size 0
            self.waves_emitted += 1
            self.last_emit_time = now

        # Expand & draw each wave
        updated_waves = []
        for size in self.waves:
            size += self.growth_speed
            if size < self.max_size:
                updated_waves.append(size)
                half = size / 2
                rect = pygame.Rect(
                    self.center[0] - half,
                    self.center[1] - half,
                    size,
                    size
                )
                pygame.draw.rect(self.display_surface, pygame.Color('white'), rect, self.thickness)

        self.waves = updated_waves

        # Deactivate when all waves are done
        if self.waves_emitted >= self.total_waves and not self.waves:
            self.active = False

class WinParticleController:
    def __init__(self, nebulons, ending_num):
        self.nebulons = nebulons
        self.ending_num = ending_num
        self.start_time = pygame.time.get_ticks()  # Record the starting time
        self.current_index = 0


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