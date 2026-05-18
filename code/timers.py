from settings import * 

class Timer:
    def __init__(self, duration, func=None, repeat=None, autostart=False):
        self.duration = duration
        self.elapsed_time = 0
        self.start_time = 0
        self.active = False
        self.func = func
        self.repeat = repeat
        self.use_delta_time = False  # Flag to use delta time (dt)

        if autostart:
            self.activate()

    def __bool__(self):
        return self.active

    def activate(self, use_dt=False):
        self.active = True
        self.elapsed_time = 0
        self.start_time = pygame.time.get_ticks()
        self.use_delta_time = use_dt

    def deactivate(self):
        self.active = False
        if self.repeat:
            self.activate(self.use_delta_time)

    def update(self, dt=None):
        if not self.active:
            return

        if self.use_delta_time and dt is not None:
            # Convert dt (seconds) to milliseconds
            self.elapsed_time += dt * 1000
            #print(f"Delta Time (ms): {dt * 1000}, Elapsed Time: {self.elapsed_time}")
        else:
            self.elapsed_time = pygame.time.get_ticks() - self.start_time

        if self.elapsed_time >= self.duration:
            if self.func:
                self.func()
            self.deactivate()

#class Timer:
#    def __init__(self, duration, func = None, repeat = None, autostart = False):
#        self.duration = duration
#        self.start_time = 0
#        self.active = False
#        self.func = func
#        self.repeat = repeat
#
#        if autostart:
#            self.activate()
#
#        self.time_passed = 0
#    
#    def __bool__(self):
#        pass
#        #return self.active
#        #allow to not add .active to check if self.active is True
#
#    def activate(self):
#        self.active = True
#        self.start_time = pygame.time.get_ticks()
#        #print('timer activated')
#
#    def deactivate(self):
#        self.active = False
#        self.start_time = 0
#        if self.repeat:
#            self.activate()
#
#
#    def update(self):
#        self.time_passed = pygame.time.get_ticks() - self.start_time
#        if self.active and (pygame.time.get_ticks() - self.start_time >= self.duration):
#            if self.func:
#                #print('function activated')
#                self.func()
#            self.deactivate()

            


