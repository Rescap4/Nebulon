from settings import * 

class Timer:
    def __init__(self, duration, func = None, repeat = None, autostart = False):
        self.duration = duration
        self.start_time = 0
        self.active = False
        self.func = func
        self.repeat = repeat

        if autostart:
            self.activate()

        self.time_passed = 0
    
    def __bool__(self):
        pass
        #return self.active
        #allow to not add .active to check if self.active is True

    def activate(self):
        self.active = True
        self.start_time = pygame.time.get_ticks()
        #print('timer activated')

    def deactivate(self):
        self.active = False
        self.start_time = 0
        if self.repeat:
            self.activate()


    def update(self):
        self.time_passed = pygame.time.get_ticks() - self.start_time
        if self.active and (pygame.time.get_ticks() - self.start_time >= self.duration):
            if self.func:
                #print('function activated')
                self.func()
            self.deactivate()
            


