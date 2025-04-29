from settings import *

class UI:
    def __init__(self, screen_dimension, menu_input, save, audio):
        self.display_surface = pygame.display.get_surface()
        self.font = pygame.font.Font("data/font_b.ttf", 18)
        self.ui_channel = pygame.mixer.Channel(2)

        
        self.switch_index = 0 # default number of selected option
        self.open_index = 0 # 0 if menu close, 1 if menu open
        self.screen_dimension = screen_dimension
        self.menu_input = menu_input
        self.save = save
        self.audio = audio
        self.state = 'map' # initial state is level for now
        self.main_menu = 'map menu' # default main menu
        self.home_text = 'Appuie sur [enter]'
        self.level_tuto_text = {2 : '[U] Annuler', 3 : '[U] Annuler', 15 : '[I] Changer', 41 : '[I] Changer'}
        self.map_text = ['[enter] selectionner', '[P] pause']
        self.level_text = '[P] pause'
        self.ending_text = "Merci d'avoir joué!"
        self.level_options = ['Continuer', 'Recommencer', 'Actions', 'Options', 'Quitter Niveau']
        self.map_options = ['Continuer', 'Tablettes', 'Options', 'Charger Partie', 'Quitter Jeu']
        self.setting_options = ['Plein Ecran [F]', 'Grille [G]', 'Tremblement [T]', 'Pause [P]', 'Selectionner [enter]'] # va afficher un tableau avec les controles en plus de ceux à toggle
        self.action_options = ['Haut [W]', 'Bas [S]', 'Gauche [A]', 'Droite [D]', 'Annuler : [U]', 'Changer : [I]']
        # dissable music, dissable sound effect, disable awakened flash?
        self.tablet_options = ['01', '02', '03', '04', '05', '06', '07', '08', '09']

    def input(self):
        keys = pygame.key.get_just_pressed()
        previous_index = self.switch_index
        back_flag = True
        if self.state == 'file':
            self.switch_index = (self.switch_index + int(keys[pygame.K_s]) - int (keys[pygame.K_w])) % len(SAVE_FILES)
            if keys[pygame.K_RETURN]:
                self.menu_input(self.state)
                self.save.info['current_file'] = (SAVE_FILES[self.switch_index])
            elif keys[pygame.K_BACKSPACE]:
                self.state = 'map'
                self.switch_index = 0
                back_flag = False

        elif self.state == 'tablet':
            self.switch_index = (self.switch_index + int(keys[pygame.K_s]) - int (keys[pygame.K_w])) % len(self.tablet_options)
            if keys[pygame.K_RETURN]:
                self.state = 'map'
                self.open_index = 0
            elif keys[pygame.K_BACKSPACE]:
                self.state = 'map'
                self.switch_index = 0
                back_flag = False

        elif self.state == 'actions':
            if keys[pygame.K_RETURN]:
                self.open_index = 0
                self.state = 'level'
            elif keys[pygame.K_BACKSPACE]:
                self.state = 'level'
                self.switch_index = 0
                back_flag = False

        elif self.state == 'options':
            self.switch_index = (self.switch_index + int(keys[pygame.K_s]) - int(keys[pygame.K_w])) % len(self.setting_options)
            if keys[pygame.K_RETURN]:
                self.menu_input(self.state)
            elif keys[pygame.K_BACKSPACE] and self.main_menu == 'map menu':
                self.state = 'map'
                self.switch_index = 0
                back_flag = False
            elif keys[pygame.K_BACKSPACE] and self.main_menu == 'level menu':
                self.state = 'level'
                self.switch_index = 0
                back_flag = False

        elif self.state == 'map':
            self.main_menu = 'map menu'
            self.switch_index = (self.switch_index + int(keys[pygame.K_s]) - int (keys[pygame.K_w])) % len(self.map_options)
            if keys[pygame.K_RETURN]:
                self.menu_input(self.state)
            if keys[pygame.K_BACKSPACE] and back_flag:
                self.open_index = 0

        elif self.state == 'level':
            self.main_menu = 'level menu'
            self.switch_index = (self.switch_index + int(keys[pygame.K_s]) - int (keys[pygame.K_w])) % len(self.level_options)
            if keys[pygame.K_RETURN]:
                self.menu_input(self.state)
            elif keys[pygame.K_BACKSPACE] and back_flag:
                self.open_index = 0

        # sound
        if keys[pygame.K_RETURN]:
            self.audio.play_sfx('select_a')
        if self.switch_index != previous_index:
            self.audio.play_sfx('click_a')
        if keys[pygame.K_BACKSPACE]:
            self.audio.play_sfx('open_menu_a')

    def level_menu(self):
        # bg
        rect = pygame.FRect(0, 0 , 400, 500) # pos, x, y
        rect.center = (self.screen_dimension.width / 2, self.screen_dimension.height / 2) # pos set to center screen
        pygame.draw.rect(self.display_surface, COLORS['black'], rect, 0)
        pygame.draw.rect(self.display_surface, COLORS['gray'], rect, 5)

        # menu
        v_offset = 0 if self.switch_index < 5 else -(self.switch_index - 3) * rect.height / 5
        for i in range(len(self.level_options)):
            x = rect.centerx
            y = rect.top + rect.height / (10) + rect.height / 5 * i + v_offset
            color = COLORS['white'] if i == self.switch_index else COLORS['gray']
            name = self.level_options[i]


            text_surf = self.font.render(name, True, color)
            text_rect = text_surf.get_frect(center = (x,y))
            if rect.collidepoint(text_rect.center):
                self.display_surface.blit(text_surf, text_rect)

    def map_menu(self):
        # bg
        rect = pygame.FRect(0, 0 , 400, 500) # pos, x, y
        rect.center = (self.screen_dimension.width / 2, self.screen_dimension.height / 2) # pos set to center screen
        pygame.draw.rect(self.display_surface, COLORS['black'], rect, 0)
        pygame.draw.rect(self.display_surface, COLORS['gray'], rect, 5)

        # menu
        v_offset = 0 if self.switch_index < 5 else -(self.switch_index - 3) * rect.height / 5
        for i in range(len(self.map_options)):
            x = rect.centerx
            y = rect.top + rect.height / (10) + rect.height / 5 * i + v_offset
            color = COLORS['white'] if i == self.switch_index else COLORS['gray']
            name = self.map_options[i]


            text_surf = self.font.render(name, True, color)
            text_rect = text_surf.get_frect(center = (x,y))
            if rect.collidepoint(text_rect.center):
                self.display_surface.blit(text_surf, text_rect)

    def file_menu(self):
        # bg
        rect = pygame.FRect(0, 0 , 400, 500) # pos, x, y
        rect.center = (self.screen_dimension.width / 2, self.screen_dimension.height / 2) # pos set to center screen
        pygame.draw.rect(self.display_surface, COLORS['black'], rect, 0)
        pygame.draw.rect(self.display_surface, COLORS['gray'], rect, 5)

        # menu
        v_offset = 0 if self.switch_index < 5 else -(self.switch_index - 3) * rect.height / 5
        for i in range(len(SAVE_FILES)):
            x = rect.centerx
            y = rect.top + rect.height / (10) + rect.height / 5 * i + v_offset
            color = COLORS['white'] if i == self.switch_index else COLORS['gray']
            name = SAVE_FILES[i]


            text_surf = self.font.render(name, True, color)
            text_rect = text_surf.get_frect(center = (x,y))
            if rect.collidepoint(text_rect.center):
                self.display_surface.blit(text_surf, text_rect)

    def tablet_menu(self):
        #number of collected tablets, curently only checked at start
        self.tablet_collected =  sum(1 for key, value in self.save.file_info.items() if key.startswith('tablet_') and value)

        # bg
        rect = pygame.FRect(0, 0 , 400, 500) # pos, x, y
        rect.center = (self.screen_dimension.width / 2 - 300, self.screen_dimension.height / 2) # pos set to center screen
        pygame.draw.rect(self.display_surface, COLORS['black'], rect, 0)
        pygame.draw.rect(self.display_surface, COLORS['gray'], rect, 5)

        # menu
        v_offset = 0 if self.switch_index < 5 else -(self.switch_index - 3) * rect.height / 5
        for i in range(len(self.tablet_options)):
            x = rect.centerx
            y = rect.top + rect.height / (10) + rect.height / 5 * i + v_offset
            color = COLORS['white'] if i == self.switch_index else COLORS['gray']
            name = self.tablet_options[i]


            text_surf = self.font.render(name, True, color)
            text_rect = text_surf.get_frect(center = (x,y))
            if rect.collidepoint(text_rect.center):
                self.display_surface.blit(text_surf, text_rect)

        # bg for the display
        display = pygame.FRect(0, 0 , 600, 500) # pos, x, y
        display.center = (self.screen_dimension.width / 2 + 300, self.screen_dimension.height / 2) # pos set to center screen
        pygame.draw.rect(self.display_surface, COLORS['black'], display, 0)
        pygame.draw.rect(self.display_surface, COLORS['gray'], display, 5)

        # text for the display
        self.render_text(display)

    def actions_menu(self):
                # bg
        rect = pygame.FRect(0, 0 , 400, 500) # pos, x, y
        rect.center = (self.screen_dimension.width / 2, self.screen_dimension.height / 2) # pos set to center screen
        pygame.draw.rect(self.display_surface, COLORS['black'], rect, 0)
        pygame.draw.rect(self.display_surface, COLORS['gray'], rect, 5)

        # menu
        v_offset = 0 if self.switch_index < 6 else -(self.switch_index - 3) * rect.height / 5
        for i in range(len(self.action_options)):
            x = rect.centerx
            y = rect.top + rect.height / (10) + rect.height / 6 * i + v_offset
            color = COLORS['white']
            name = self.action_options[i]


            text_surf = self.font.render(name, True, color)
            text_rect = text_surf.get_frect(center = (x,y))
            if rect.collidepoint(text_rect.center):
                self.display_surface.blit(text_surf, text_rect)

    def options_menu(self):
        # bg
        rect = pygame.FRect(0, 0 , 400, 500) # pos, x, y
        rect.center = (self.screen_dimension.width / 2, self.screen_dimension.height / 2) # pos set to center screen
        pygame.draw.rect(self.display_surface, COLORS['black'], rect, 0)
        pygame.draw.rect(self.display_surface, COLORS['gray'], rect, 5)

        # menu
        v_offset = 0 if self.switch_index < 5 else -(self.switch_index - 3) * rect.height / 5
        for i in range(len(self.setting_options)):
            x = rect.centerx
            y = rect.top + rect.height / (10) + rect.height / 5 * i + v_offset
            color = COLORS['white'] if i == self.switch_index else COLORS['gray']
            name = self.setting_options[i]


            text_surf = self.font.render(name, True, color)
            text_rect = text_surf.get_frect(center = (x,y))
            if rect.collidepoint(text_rect.center):
                self.display_surface.blit(text_surf, text_rect)

    def home_info(self):
                # bg
        rect = pygame.FRect(0, 0 , 100, 100) # pos, x, y
        rect.center = (self.screen_dimension.width / 2, self.screen_dimension.height - 50) # pos set to center screen

        x = rect.centerx
        y = rect.top + rect.height / (10)
        color = COLORS['white']
        name = self.home_text
        text_surf = self.font.render(name, True, color)
        text_rect = text_surf.get_frect(center = (x,y))
        if rect.collidepoint(text_rect.center):
            self.display_surface.blit(text_surf, text_rect)

    def map_info(self):
            # bg
        rect = pygame.FRect(0, 0 , 100, 200) # pos, x, y
        rect.center = (self.screen_dimension.width - 180, 120) # pos set to center screen

        # menu
        v_offset = 0 if self.switch_index < 5 else -(self.switch_index - 3) * rect.height / 5
        for i in range(len(self.map_text)):
            x = rect.centerx
            y = rect.top + rect.height / (10) + rect.height / 5 * i + v_offset
            color = COLORS['white']
            name = self.map_text[i]


            text_surf = self.font.render(name, True, color)
            text_rect = text_surf.get_frect(center = (x,y))
            if rect.collidepoint(text_rect.center):
                self.display_surface.blit(text_surf, text_rect)

    def level_info(self):
        # bg
        rect = pygame.FRect(0, 0 , 100, 200) # pos, x, y
        rect.center = (self.screen_dimension.width - 120, 120) # pos set to center screen

        # menu
        x = rect.centerx
        y = rect.top + rect.height / (10)
        color = COLORS['white']
        name = self.level_text
        text_surf = self.font.render(name, True, color)
        text_rect = text_surf.get_frect(center = (x,y))
        if rect.collidepoint(text_rect.center):
            self.display_surface.blit(text_surf, text_rect)

    def ending_info(self):
        # bg
        ending_font = pygame.font.Font("data/font_b.ttf", 50)
        rect = pygame.FRect(0, 0 , 100, 100) # pos, x, y
        rect.center = (self.screen_dimension.width / 2, self.screen_dimension.height / 2) # pos set to center screen

        x = rect.centerx
        y = rect.top + rect.height / (10)
        color = COLORS['white']
        name = self.ending_text
        text_surf = ending_font.render(name, True, color)
        text_rect = text_surf.get_frect(center = (x,y))
        if rect.collidepoint(text_rect.center):
            self.display_surface.blit(text_surf, text_rect)

    def level_tuto(self, level_num):
        # bg
        rect = pygame.FRect(0, 0 , 100, 200) # pos, x, y
        rect.center = (self.screen_dimension.width - 120, 160) # pos set to center screen

        # menu
        x = rect.centerx
        y = rect.top + rect.height / (10)
        color = COLORS['white']
        name = self.level_tuto_text[level_num]
        text_surf = self.font.render(name, True, color)
        text_rect = text_surf.get_frect(center = (x,y))
        if rect.collidepoint(text_rect.center):
            self.display_surface.blit(text_surf, text_rect)

    def render_text(self, display):
        font = pygame.font.Font(TEXT_SETTINGS["font_name"], TEXT_SETTINGS["font_size"])
        rect = display

        # Get text based on whether the tablet has been collected
        if self.switch_index < self.tablet_collected:
            text = TEXT_TABLETS[self.switch_index]
        else:
            text_surface = font.render("???", True, TEXT_SETTINGS["text_color"])
            text_rect = text_surface.get_rect(center=rect.center)
            self.display_surface.blit(text_surface, text_rect)
            return  # Skip the rest of the function since we're done


        words = text.split()
        line_height = font.get_height() + TEXT_SETTINGS["line_spacing"]
        lines = []
        current_line = ""

        for word in words:
            test_line = current_line + word + " "
            if font.size(test_line)[0] < rect.width - (2 * TEXT_SETTINGS["padding_x"]):  # Account for left/right padding
                current_line = test_line
            else:
                lines.append(current_line)
                current_line = word + " "

        lines.append(current_line)  # Add last line

        y = rect.y + TEXT_SETTINGS["padding_y"]  # Start at top with padding
        for line in lines:
            if y + line_height > rect.y + rect.height - TEXT_SETTINGS["padding_y"]:  # Stop if text overflows
                break
            text_surface = font.render(line, True, TEXT_SETTINGS["text_color"])
            self.display_surface.blit(text_surface, (rect.x + TEXT_SETTINGS["padding_x"], y))
            y += line_height  # Move down for next line

    def update(self):
        if self.open_index == 1:
            self.input()

    def draw(self):
        match self.state:
            case 'home' :self.home_menu()
            case 'map': self.map_menu()
            case 'level': self.level_menu()
            case 'file': self.file_menu()
            case 'tablet': self.tablet_menu()
            case 'actions' : self.actions_menu()
            case 'options': self.options_menu()
