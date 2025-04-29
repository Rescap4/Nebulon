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
        pygame.init()
        pygame.mixer.init()
        pygame.display.set_caption('Nebulon')
        self.display_surface = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        self.clock = pygame.time.Clock()
        self.running = True

        # load game  
        self.load_assets()

        # For full screen
        self.screen_dimension = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        self.is_full_screen = False
        
        # tests for overworld
        self.tmx_home = load_pygame(join('data', 'maps', 'home.tmx'))
        self.tmx_overworld = load_pygame(join('data', 'maps', 'overworld.tmx'))
        self.tmx_ending = load_pygame(join('data', 'maps', 'final_scene.tmx'))
        self.tmx_maps = {}
        self.audio_files = {}
        self.level_files = self.get_level_files()

        # for save
        self.save = Save(self.level_files)
        # for audio
        self.audio = AudioManager()
        #self.audio.mute_music()
        #self.audio.mute_looped()
        #self.audio.mute_looped()
        self.audio.play_music('music_theme_b')
        # for data

        self.data = Data()
        # for menu
        self.ui = UI(self.screen_dimension, self.menu_input, self.save, self.audio)

        #self.tmx_maps[41] = load_pygame(join('data', 'maps', 'level_41.tmx'))
        #self.current_stage = Level(self.tmx_maps[41], self.save, self.data, self.level_frames, self.audio, self.switch_level, self.screen_dimension)
        #self.current_stage = Overworld(self.tmx_overworld, self.save, self.data, self.overworld_frames, self.audio, self.switch_level, self.screen_dimension) # + data and overworld frames dans le tuto
        #self.current_stage = Cutscene(self.tmx_ending, self.save, self.data, self.cutscene_frames, self.audio, self.switch_level, self.screen_dimension)

        self.current_stage = Home(self.tmx_home, self.save, self.data, self.home_frames, self.audio, self.switch_level, self.screen_dimension)

        # ideally be in the save files?
        self.music_flag = True
        self.sfx_flag = True

    def get_level_files(self):
        """Retrieve and sort level files once at initialization."""
        levels_path = join('data', 'maps')
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
            'tablet' : import_image('images', 'objects', 'tablet_f'),
            'spike' :  import_image('images', 'objects', 'spike_b'),

            'pink' : import_image('images', 'backgrounds', 'pink_e', alpha = False),
            'green' : import_image('images', 'backgrounds', 'green_a', alpha = False),
            'orange' : import_image('images', 'backgrounds', 'orange_g', alpha = False),
            'blue' : import_image('images', 'backgrounds', 'blue_b', alpha = False),
            'black' : import_image('images', 'backgrounds', 'black_b', alpha = False)
        }
        
        self.overworld_frames = {
            'node_numbers' : import_folder('images', 'numbers'),
            'icon' : import_image('images', 'objects', 'icon_a'),
            'background' : import_image('images', 'backgrounds', 'map_a', alpha = False)
        }

        self.home_frames = {
            'background' : import_image('images', 'backgrounds', 'map_a', alpha = False),
            'title' : import_image('images', 'backgrounds', 'title_a')
        }

        self.cutscene_frames = {
            'player' : import_folder('images', 'player'),
            'background' : import_image('images', 'backgrounds', 'map_a', alpha = False),
        }

        #self.audio['select_a'].set_volume(0.3)
        #self.audio['error_007'].set_volume(0.05)
        #self.audio['undo_d'].set_volume(0.3)
        
    def switch_level(self, target, screen_dimension, unlock = 0):
        # Dont execute if save isnt loaded
        if not hasattr(self.save, 'file_info') or 'icon_pos' not in self.save.file_info:
            print('[Warning] Save not ready — switch_level aborted.')
            return False

        if target == 'level':
            self.current_stage = Level(self.tmx_maps[self.data.current_level], self.save, self.data, self.level_frames, self.audio, self.switch_level, self.screen_dimension) #
            self.ui.state = 'level'

        elif target == 'home':
            self.current_stage = Home(self.tmx_home, self.save, self.data, self.home_frames, self.audio, self.switch_level, self.screen_dimension)

        elif target == 'cutscene':
            self.current_stage = Cutscene(self.tmx_ending, self.save, self.data, self.level_frames, self.audio, self.switch_level, self.screen_dimension)

        else: # overworld
            self.current_stage = Overworld(self.tmx_overworld, self.save, self.data, self.overworld_frames, self.audio, self.switch_level, self.screen_dimension) # , -1) to not unlock new levels
            self.ui.state = 'map'

        self.general_music()
        return True

    def general_text(self):
        if isinstance(self.current_stage, Level):
            self.ui.level_info()
            if self.current_stage.level_num in self.ui.level_tuto_text:
                self.ui.level_tuto(self.current_stage.level_num)

        elif isinstance(self.current_stage, Overworld):
            self.ui.map_info()
            
        elif isinstance(self.current_stage, Home):
            self.ui.home_info()

        elif isinstance(self.current_stage, Cutscene):
            self.ui.ending_info()
        
    def general_music(self):
        current_stage_name = self.current_stage.__class__.__name__

        if current_stage_name == 'Overworld':
            if self.old_stage in ['Home', 'Level']:
                self.audio.play_music('music_theme_b')
                self.audio.stop_loop()

        elif current_stage_name == 'Level' and self.old_stage == 'Overworld':
            match self.current_stage.bg_color:
                case 'pink':   self.audio.play_music('music_pink_b')
                case 'green':  self.audio.play_music('music_green_a')
                case 'orange': self.audio.play_music('music_orange_a')
                case 'blue':   self.audio.play_music('music_blue_a')
                case 'black':  self.audio.play_music('music_black_a')

        self.old_stage = current_stage_name

    def open_menu(self):
        """Draw the menu and prevent movement while open."""
        if self.transition_frames > 0:
            self.transition_frames -= 1
            if self.transition_frames == 0:
                self.current_stage.update_flag = True
        elif self.ui.open_index == 1:
            self.ui.draw()
            self.current_stage.update_flag = False
        else:
            self.current_stage.update_flag = True

    def tablet_count(self):
        #number of collected tablets, curently only checked at start
        self.tablet_collected =  sum(1 for key, value in self.save.file_info.items() if key.startswith('tablet_') and value)
        #print(self.tablet_collected)
             
    def menu_input(self, state):
        # map options
        map_flag = True
        level_flag = True
        if isinstance(self.current_stage, Overworld): 
            if self.ui.state == 'map':
                map_flag = False
                match self.ui.map_options[self.ui.switch_index]:
                    case 'Continuer':
                        self.ui.open_index = 0
                    case 'Charger Partie':
                        self.ui.open_index = 0
                        self.ui.state = 'file'
                        self.ui.open_index = 1
                        self.ui.switch_index = 0
                    case 'Tablettes':
                        self.tablet_count()
                        self.ui.state = 'tablet'
                        self.ui.switch_index = 0
                    case 'Options':
                        self.ui.state = 'options'
                        self.ui.switch_index = 0
                    case 'Quitter Jeu':
                        self.ui.open_index = 0
                        self.switch_level('home', self.screen_dimension)

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
                match self.ui.level_options[self.ui.switch_index]:
                    case 'Continuer':
                        self.ui.open_index = 0
                    case 'Recommencer': 
                        self.ui.open_index = 0
                        self.switch_level('level', self.screen_dimension)
                    case 'Quitter Niveau': 
                        self.switch_level('overworld', 0)
                        self.ui.state = 'map'
                        self.ui.open_index = 0
                    case 'Actions':
                        self.ui.state = 'actions'
                        self.ui.switch_index = 0
                    case 'Options':
                        self.ui.state = 'options'
                        self.ui.switch_index = 0

            elif self.ui.state == 'options' and level_flag:
                    self.option_trigger()
                    self.ui.state = 'level'
                    self.ui.open_index = 0
                    self.ui.switch_index = 0

    def option_trigger(self):
        # include a sound to show that it worked
        match self.ui.setting_options[self.ui.switch_index]:
            case 'Plein Ecran [F]':
                self.full_screen()
            case 'Grille [G]':
                self.save.file_info['grid'] = not self.save.file_info['grid']
            case 'Tremblement [T]':
                self.save.file_info['shake'] = not self.save.file_info['shake']
            case 'Pause [P]':
                self.ui.open_index = 0
            case 'Selectionner [enter]':
                self.ui.open_index = 0

    def activate_pause(self):    
        self.ui.switch_index = 0
        self.ui.open_index = (self.ui.open_index + 1) % 2
        self.audio.play_sfx('open_menu_a')
        #self.audio['sfx'].play(self.audio['open_menu_a'])
        if self.ui.open_index == 0:
            
            if self.ui.main_menu == 'level menu':
                self.ui.state = 'level'
            if self.ui.main_menu == 'map menu':
                self.ui.state = 'map'
        
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


        # update screen size
        self.is_full_screen = not self.is_full_screen
        if self.is_full_screen:
            self.screen_dimension = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
        else:
            self.screen_dimension = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        self.audio.play_sfx('select_a')
        self.current_stage.background()

    def toggle_music(self):
        self.music_flag = not self.music_flag
        if self.music_flag:
            self.audio.unmute_music()
        else: 
            self.audio.mute_music()

    def dimension_check(self):
        if self.is_full_screen:
            self.current_stage.camera = self.current_stage.camera2
        else:
            self.current_stage.camera = self.current_stage.camera1

    def run(self):
        while self.running:
            dt = self.clock.tick(FRAMERATE) / 1000 
            keys = pygame.key.get_just_pressed()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    with open(join('data', 'save_file.txt'), 'w') as save_file:
                        json.dump(self.save.info, save_file)
                    self.running = False
            if keys[pygame.K_p] and not isinstance(self.current_stage, Home):
                self.activate_pause()
            if keys[pygame.K_f]:
                self.full_screen()
            if keys[pygame.K_m]:
                self.toggle_music()

            self.current_stage.run(dt)
            self.load_level()
            self.ui.update()
            self.save.update()
            self.dimension_check()
            self.general_text()
            self.open_menu()

            # debug section
            #debug(round(self.clock.get_fps()))
            #debug(f'open index  {self.ui.state}', 10)
            #debug(f'open index  {self.ui.open_index}', 30)
            #debug(f'switch index  {self.ui.switch_index}', 50)

            #debug(f'flag is  {self.current_stage.update_flag}', 50)
            
            pygame.display.update()
        
        pygame.quit()
 
if __name__ == '__main__':
    game = Game()
    game.run() 