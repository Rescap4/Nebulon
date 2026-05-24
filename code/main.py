from settings import *
from sprites import *
from support import *
from debug import *
from ui import UI
from groups import AllSprites
from overworld import Overworld
from level import Level
from home import Home
from cutscene import Cutscene
from save import Save
from audio import AudioManager
from data import Data


class Game:
    def __init__(self):
        pygame.mixer.pre_init(44100, -16, 2, 512)
        pygame.init()
        pygame.mixer.init()
        pygame.mouse.set_visible(False)
        pygame.display.set_caption('Nebulon')
        self.display_surface = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        self.clock = pygame.time.Clock()
        self.running = True

        # load game  
        self.load_assets()

        # For full screen
        self.screen_dimension = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SCALED)
        self.is_full_screen = False

        # Utiliser BASE_PATH pour les fichiers TMX
        from support import BASE_PATH
        self.tmx_home = load_pygame(join(BASE_PATH, 'data', 'maps', 'home.tmx'))
        self.tmx_overworld = load_pygame(join(BASE_PATH, 'data', 'maps', 'overworld.tmx'))
        self.tmx_ending_1 = load_pygame(join(BASE_PATH, 'data', 'maps', 'ending_1.tmx'))
        self.tmx_ending_2 = load_pygame(join(BASE_PATH, 'data', 'maps', 'ending_2.tmx'))

        self.tmx_maps = {}
        self.audio_files = {}
        self.level_files = self.get_level_files()

        self.save = Save(self.level_files)
        self.audio = AudioManager()
        self.data = Data()
        
        self.current_stage = Home(self.tmx_home, self.save, self.data, self.home_frames, self.audio, self.switch_level, self.screen_dimension)
        self.ui = UI(self.screen_dimension, self.menu_input, self.save, self.audio, get_stage=lambda: self.current_stage.level_num)

        #self.current_stage = Level(load_pygame(join('data', 'maps', 'lvl_26_2.tmx')), self.save, self.data, self.home_frames, self.audio, self.switch_level, self.screen_dimension)

        
        self.music_flag = True
        self.sfx_flag = True

        self.fade_oppacity = 0
        # OLD: self.fade_surf = pygame.Surface(FULL_SCREEN_SIZE)
        self.fade_surf = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
        self.fade_surf.fill((0,0,0))
        self.fade_surf.set_alpha(0)

        self.general_music()

    def fade_out(self):
        level = isinstance(self.current_stage, Level) and self.current_stage.level_num in [0, 70]
        cutscene = isinstance(self.current_stage, Cutscene)

        if level or cutscene:
            if level:
                if self.current_stage.end_timer.active:
                    self.fade_oppacity = min(self.fade_oppacity + 2, 255)  # Fade-in with a max value of 255

            if cutscene:
                if self.current_stage.cutscene_timer.elapsed_time <= 17000:
                    self.fade_oppacity = max(self.fade_oppacity - 2, 0)  # Fade-out after 8000ms

                else:
                    self.fade_oppacity = min(self.fade_oppacity + 2, 255)  # Continue fading in until fully visible

            self.fade_surf.set_alpha(self.fade_oppacity)
            self.display_surface.blit(self.fade_surf, (0, 0))

    def get_level_files(self):
        """Retrieve and sort level files once at initialization."""
        from support import BASE_PATH
        levels_path = join(BASE_PATH, 'data', 'maps')
        self.level_files = glob(join(levels_path, "level_*.tmx"))

        def extract_number(filename):
            match = re.search(r'level_(\d+)\.tmx', filename)
            levels = int(match.group(1)) if match else float('inf')
            return levels

        self.level_files.sort(key=extract_number)
        return self.level_files
    
    def load_level(self):
        """Load the current level if it isn't already loaded."""
        if isinstance(self.current_stage, Overworld):
            current_level = self.data.current_level
            if current_level not in self.tmx_maps:
                # Find the file corresponding to the current level
                def extract_number(filename):
                    match = re.search(r'level_(\d+)\.tmx', filename) # could switch to lvl_ once levels are numbered
                    return int(match.group(1)) if match else None
                level_file = next((file for file in self.level_files if extract_number(file) == current_level), None)
                if level_file:
                    self.tmx_maps[current_level] = load_pygame(level_file)
                    self.data.levels_imported.append(current_level)

    def load_assets(self):
        # general
        self.old_stage = 'Home'
        self.tablet_collected = 0
        self.transition_frames = 0

        # graphics 
        self.player_frames = import_folder('images', 'player')
        self.node_numbers = import_folder('images', 'numbers')

        self.level_frames = {
            'player' : import_folder('images', 'player'),
            'box' : import_image('images', 'objects', 'box_a'),
            'battery' : import_image('images', 'objects', 'battery_c'), 
            'behind' : import_image('images', 'objects', 'behind_g'),
            'tablet' : import_image('images', 'objects', 'tablet_f'),
            'spike' :  import_image('images', 'objects', 'spike_c'),

            'pink' : import_image('images', 'backgrounds', 'pink_e', alpha = False),
            'green' : import_image('images', 'backgrounds', 'green_a', alpha = False),
            'orange' : import_image('images', 'backgrounds', 'orange_g', alpha = False),
            'blue' : import_image('images', 'backgrounds', 'blue_b', alpha = False),
            'black' : import_image('images', 'backgrounds', 'black_c', alpha = False)
        }
        
        self.overworld_frames = {
            'node_numbers' : import_folder('images', 'numbers'),
            'node_grounds' : import_image('data', 'tilesets', 'grounds_f'),
            'icon' : import_image('images', 'objects', 'icon_a'),
            'background' : import_image('images', 'backgrounds', 'map_a', alpha = False)
        }

        self.home_frames = {
            'background' : import_image('images', 'backgrounds', 'map_a', alpha = False),
            'title' : import_image('images', 'backgrounds', 'title_a')
        }

        self.cutscene_frames = {
            'player' : import_folder('images', 'player'),
            'background' : import_image('images', 'backgrounds', 'ending_a', alpha = False),
        }
        
    def switch_level(self, target, screen_dimension, unlock = 0):
        # Dont execute if save isnt loaded
        if not hasattr(self.save, 'file_info') or 'icon_pos' not in self.save.file_info:
            #print('[Warning] Save not ready — switch_level aborted.')
            return False

        if target == 'level':
            self.current_stage = Level(self.tmx_maps[self.data.current_level], self.save, self.data, self.level_frames, self.audio, self.switch_level, self.screen_dimension)
            self.ui.state = 'level'
            self.fade_oppacity = 0

        elif target == 'home':
            self.current_stage = Home(self.tmx_home, self.save, self.data, self.home_frames, self.audio, self.switch_level, self.screen_dimension)

        elif target == 'cutscene':
            ending_num = self.current_stage.cutscene_index
            self.current_stage = Cutscene(getattr(self, f"tmx_ending_{ending_num}"), self.save, self.data, self.cutscene_frames, self.audio, self.switch_level, self.screen_dimension, ending_num)
            self.ui.scrolling_text_y_positions = [-1600 + i * 150 for i in range(len(self.ui.ending_text_1[self.ui.language]))] # reset it
            self.ui.open_index = 0
            self.audio.stop_loop()

        else: # overworld
            self.ui.state = 'map'
            self.audio.stop_loop()
            self.tablet_count()
            self.current_stage = Overworld(self.tmx_overworld, self.save, self.data, self.overworld_frames, self.audio, self.switch_level, self.screen_dimension) # , -1) to not unlock new levels

        self.general_music()
        return True

    def general_text(self, dt):
        if isinstance(self.current_stage, Level):
            self.ui.level_info()
            if self.current_stage.level_num in self.ui.level_tuto_text:
                self.ui.level_tuto(self.current_stage.level_num)

        elif isinstance(self.current_stage, Overworld):
            self.ui.map_info()
            
        elif isinstance(self.current_stage, Home):
            self.ui.home_info()

        elif isinstance(self.current_stage, Cutscene):
            ending_num = self.current_stage.ending_num
            if self.current_stage.ending_num == 1:
                self.ui.ending_info(dt, ending_num)
            else:
                self.ui.ending_info(dt, ending_num)
        
    def general_music(self):
        current_stage_name = self.current_stage.__class__.__name__
        if not self.music_flag:
            return
        elif current_stage_name in ['Home', 'Overworld']:
            self.audio.play_music('music_theme_b')
            self.audio.stop_loop()

        elif current_stage_name == 'Level':# and self.old_stage == 'Overworld':
            match self.current_stage.bg_color:
                case 'pink':   self.audio.play_music('music_pink_b')
                case 'green':  self.audio.play_music('music_green_a')
                case 'orange': self.audio.play_music('music_orange_a')
                case 'blue':   self.audio.play_music('music_blue_a')
                case 'black':  self.audio.play_music('music_black_a')
        
        elif current_stage_name == 'Cutscene':
            self.audio.play_music('victory_b', loops = 0)

        #self.old_stage = current_stage_name

    def open_menu(self):
        """Draw the menu and prevent movement while open."""
        if self.transition_frames > 0:
            self.transition_frames -= 1
            if self.transition_frames == 0:
                self.current_stage.update_flag = True
        elif self.ui.open_index == 1:
            self.ui.draw()
            #self.ui.pause_info()
            self.current_stage.update_flag = False
        else:
            self.current_stage.update_flag = True

    def tablet_count(self):
        #number of collected tablets, curently only checked at start
        self.tablet_collected =  sum(1 for key, value in self.save.file_info.items() if key.startswith('tablet_') and value)

        if self.tablet_collected >= 7 and 'level_0' not in self.save.file_info:
            self.save.file_info[f'level_0'] = False
             
    def menu_input(self, state):
        # map options
        map_flag = True
        level_flag = True
        if isinstance(self.current_stage, Overworld): 
            if self.ui.state == 'map':
                map_flag = False
                match self.ui.switch_index:
                    case 0: # continue
                        self.ui.open_index = 0
                    case 1: # tablet
                        self.tablet_count()
                        self.ui.state = 'tablet'
                        self.ui.switch_index = 0
                    case 2: # options
                        self.ui.state = 'options'
                        self.ui.switch_index = 0
                    case 3: # change file
                        self.ui.open_index = 0
                        self.ui.state = 'file'
                        self.ui.open_index = 1
                        self.ui.switch_index = 0
                    case 4: # quit game
                        self.ui.open_index = 0
                        self.running = False

            elif self.ui.state == 'options' and map_flag:
                self.option_trigger()
                self.ui.state = 'map'
                self.ui.open_index = 0
                self.ui.switch_index = 0

            elif self.ui.state == 'file'and map_flag:
                self.ui.open_index = 0
                self.ui.state = 'map'
                self.switch_level('home', self.screen_dimension)

                                        
        # level options
        elif isinstance(self.current_stage, Level):
            if self.ui.state == 'level':
                level_flag = False
                match self.ui.switch_index:
                    case 0: # continue
                        self.ui.open_index = 0
                    case 1: # restart
                        self.ui.open_index = 0
                        self.switch_level('level', self.screen_dimension)
                    case 2: # hint
                        self.ui.state = 'indice'
                        self.ui.switch_index = 0
                    case 3: # options
                        self.ui.state = 'options'
                        self.ui.switch_index = 0
                    case 4: # overworld
                        self.switch_level('overworld', 0)
                        self.ui.state = 'map'
                        self.ui.open_index = 0

            elif self.ui.state == 'options' and level_flag:
                    self.option_trigger()
                    self.ui.state = 'level'
                    self.ui.open_index = 0
                    self.ui.switch_index = 0

    def option_trigger(self):
        # include a sound to show that it worked
        match self.ui.switch_index:
            case 0: # full screen
                self.full_screen()
            case 1: # gid
                self.save.file_info['grid'] = not self.save.file_info['grid']
            case 2: # shake
                self.save.file_info['shake'] = not self.save.file_info['shake']
            case 3: # music
                self.toggle_music()
            #case 4: # sound effect # replaced with language
            #    self.toggle_sound()
            case 4: # language
                self.change_language()

    def activate_pause(self):
        #self.audio.stop_sfx()
        if isinstance(self.current_stage, Overworld) or isinstance(self.current_stage, Level):
            self.ui.switch_index = 0
            self.ui.open_index = (self.ui.open_index + 1) % 2
            self.audio.play_sfx('open_menu_a')
            if self.ui.open_index == 0:

                if self.ui.main_menu == 'level menu':
                    self.ui.state = 'level'
                if self.ui.main_menu == 'map menu':
                    self.ui.state = 'map'
        else:
            self.audio.play_sfx('error_a')
        
    def full_screen(self):
        # to prevent clipping
        if self.transition_frames > 0:
            return
        if hasattr(self.current_stage, 'player_sprites'):
            for player in self.current_stage.player_sprites:
                if player.direction != [0, 0]:
                    self.audio.play_sfx('error_a')
                    return
        if hasattr(self.current_stage, 'box_sprites'):
            for box in self.current_stage.box_sprites:
                if box.direction != [0, 0]:
                    self.audio.play_sfx('error_a')
                    return
                

        self.current_stage.update_flag = False
        self.transition_frames = 5
    
        self.is_full_screen = not self.is_full_screen
    
        if self.is_full_screen:
            # Detect the monitor's native resolution.
            desktop_sizes = getattr(pygame.display, "get_desktop_sizes", None)
            if callable(desktop_sizes):
                monitor_w, monitor_h = desktop_sizes()[0]
            else:
                info = pygame.display.Info()
                monitor_w, monitor_h = info.current_w, info.current_h

            # Compute a logical size that exactly matches the monitor's aspect ratio
            # so pygame.SCALED fills the screen with zero black bars.
            # We keep whichever game dimension is the bottleneck and expand the other:
            # - monitor wider than game  → expand logical width,  keep height
            # - monitor taller than game → expand logical height, keep width
            if monitor_w / monitor_h > WINDOW_WIDTH / WINDOW_HEIGHT:
                fs_w = round(WINDOW_HEIGHT * monitor_w / monitor_h)
                fs_h = WINDOW_HEIGHT
            else:
                fs_w = WINDOW_WIDTH
                fs_h = round(WINDOW_WIDTH * monitor_h / monitor_w)

            fs_w = min(fs_w, 30 * TILE_SIZE)  # cap at 1920
            fs_h = min(fs_h, 19 * TILE_SIZE)  # cap at 1216

            self.screen_dimension = pygame.display.set_mode(
                (fs_w, fs_h),
                pygame.FULLSCREEN | pygame.SCALED
            )
        else:
            # Retour fenêtré avec SCALED
            self.screen_dimension = pygame.display.set_mode(
                (WINDOW_WIDTH, WINDOW_HEIGHT),
                pygame.SCALED
            )
    
        self.audio.play_sfx('select_a')
        self.current_stage.background()

    def toggle_music(self):
        self.music_flag = not self.music_flag
        if self.music_flag:
            self.general_music()
        else: 
            self.audio.stop_music()
            self.audio.current_music_key = None

    def toggle_sound(self):
        self.sfx_flag = not self.sfx_flag
        if self.sfx_flag:
            self.audio.unmute_looped()
            self.audio.unmute_sfx()
        else: 
            self.audio.mute_looped()
            self.audio.mute_sfx()

    def change_language(self):
        if self.ui.language == 'fr':
            self.save.file_info['language'] = 'eng'
        else:
            self.save.file_info['language'] = 'fr'

    def dimension_check(self):
        # OLD: switched to camera2 because the fullscreen logical size was 1920×1200,
        # requiring a different viewport offset to re-center the level content.
        # if self.is_full_screen:
        #     self.current_stage.camera = self.current_stage.camera2
        # else:
        #     self.current_stage.camera = self.current_stage.camera1

        # NEW: logical size is always WINDOW_WIDTH×WINDOW_HEIGHT, so camera1 is
        # always correct and the level stays centered in both windowed and fullscreen.
        self.current_stage.camera = self.current_stage.camera1

    def run(self):
        while self.running:
            dt = self.clock.tick_busy_loop(FRAMERATE) / 1000 
            dt = min(dt, 1/30)
            keys = pygame.key.get_just_pressed()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    with open(join('data', 'save_file.txt'), 'w') as save_file:
                         json.dump(self.save.info, save_file)
                    self.running = False

            if keys[pygame.K_p] or keys[pygame.K_ESCAPE]:
                self.activate_pause()
            if keys[pygame.K_f]:
                self.full_screen()
            #if keys[pygame.K_m]:
            #    self.toggle_music()
            #if keys[pygame.K_n]:
            #    self.toggle_sound()
            #if keys[pygame.K_l]:
            #    self.change_language()

            self.current_stage.run(dt)
            self.load_level()
            self.ui.update()
            self.save.update()
            self.dimension_check()
            self.general_text(dt)
            self.open_menu()
            self.fade_out()

            # debug section
            #debug(round(self.clock.get_fps()))
            #debug(self.current_stage.update_flag)
            pygame.display.update()
        
        pygame.time.wait(200)
        pygame.quit()

if __name__ == '__main__':
    game = Game()
    game.run() 