from settings import *

class UI:
    def __init__(self, screen_dimension, menu_input, save, audio, get_stage):
        self.display_surface = pygame.display.get_surface()
        self.font = pygame.font.Font(join(BASE_PATH, "data", "font_b.ttf"), 18)
        self.ui_channel = pygame.mixer.Channel(2)

        #self.level_num = f"Level {level_num}"
        self.get_stage = get_stage

        self.switch_index = 0 # default number of selected option
        self.open_index = 0 # 0 if menu close, 1 if menu open
        self.screen_dimension = screen_dimension
        self.menu_input = menu_input
        self.save = save
        self.language = self.save.file_info['language']
        self.audio = audio
        self.ending_index = 0
        self.state = 'map' # initial state is level for now
        self.main_menu = 'map menu' # default main menu
        self.home_text = {'fr':'Appuie sur [enter]','eng':'Press [enter]'}
        self.level_tuto_text = {
            2:  {'fr': '[U] Annuler', 'eng': '[U] Cancel'},
            3:  {'fr': '[U] Annuler', 'eng': '[U] Cancel'},
            15: {'fr': '[I] Changer', 'eng': '[I] Change'},
            41: {'fr': '[I] Changer', 'eng': '[I] Change'},
        }
        self.map_text = [
            {'fr': '[enter] Selectionner', 'eng': '[enter] Select'},
            {'fr': '[P] Pause',            'eng': '[P] Pause'},
        ]
        self.level_text = '[P] Pause'
        self.ending_text_1 = {'fr':["Les défis ne font que commencer...","","","","","","","","","","", "Merci d'avoir joué!"], 
                              'eng':["Challenges are only begenning...","","","","","","","","","","", "Thank you for playing!"]}
        self.ending_text_2 = {'fr':["","","Ils vous remercient infiniment!","","","Tout les nébulons sont unis","Grâce à vous","","","","", "Félicitation!"],
                                'eng':["","","They thank you infinitely!","","","All nebulons are united","Thanks to you","","","","", "Congratulations!"]}
        self.level_options = {'fr':['Continuer', 'Recommencer', 'Indice', 'Options', 'Quitter Niveau'],
                              'eng':['Continue', 'Restart', 'Hint', 'Options', 'Quit Level']}
        self.map_options = {'fr':['Continuer', 'Tablettes', 'Options', 'Charger Partie', 'Quitter Jeu'],
                            'eng':['Continue', 'Tablets', 'Options', 'Load File', 'Quit Game']}
        self.setting_options = {'fr':['Plein Ecran [F]', 'Grille [G]', 'Tremblement [T]', 'Musique', 'Langue'],
                                'eng':['Full Screen [F]', 'Grid [G]', 'Shake [T]', 'Music', 'Language']}
        self.action_options = {'fr':['Haut [W]', 'Bas [S]', 'Gauche [A]', 'Droite [D]', 'Annuler : [U]', 'Changer : [I]'], # unused
                               'eng':['Up [W]', 'Down [S]', 'Left [A]', 'Right [D]', 'Undo : [U]', 'Change : [I]']}
        self.tablet_options = ['01', '02', '03', '04', '05', '06', '07', '08']


    def input(self):
        keys = pygame.key.get_just_pressed()
        previous_index = self.switch_index
        back_flag = True
        if self.state == 'file':
            self.switch_index = (self.switch_index + int(keys[pygame.K_s]) + int(keys[pygame.K_DOWN]) - int (keys[pygame.K_w]) - int(keys[pygame.K_UP])) % len(SAVE_FILE_NAMES[self.language])

            if keys[pygame.K_RETURN] or keys[pygame.K_SPACE]:
                self.menu_input(self.state) 
                self.save.info['current_file'] = (SAVE_FILES[self.switch_index])
                
            elif keys[pygame.K_BACKSPACE]:
                self.state = 'map'
                self.switch_index = 0
                back_flag = False

        elif self.state == 'tablet':
            self.switch_index = (self.switch_index + int(keys[pygame.K_s]) + int(keys[pygame.K_DOWN]) - int (keys[pygame.K_w]) - int(keys[pygame.K_UP])) % len(TEXT_TABLETS[self.language])
            if keys[pygame.K_RETURN] or keys[pygame.K_SPACE]:
                self.state = 'map'
                self.open_index = 0
            elif keys[pygame.K_BACKSPACE]:
                self.state = 'map'
                self.switch_index = 0
                back_flag = False

        elif self.state == 'indice':
            if keys[pygame.K_RETURN] or keys[pygame.K_SPACE]:
                self.open_index = 0
                self.state = 'level'
            elif keys[pygame.K_BACKSPACE]:
                self.state = 'level'
                self.switch_index = 0
                back_flag = False

        elif self.state == 'options':
            self.switch_index = (self.switch_index + int(keys[pygame.K_s]) + int(keys[pygame.K_DOWN]) - int (keys[pygame.K_w]) - int(keys[pygame.K_UP])) % len(self.setting_options[self.language])
            if keys[pygame.K_RETURN] or keys[pygame.K_SPACE]:
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
            self.switch_index = (self.switch_index + int(keys[pygame.K_s]) + int(keys[pygame.K_DOWN]) - int (keys[pygame.K_w]) - int(keys[pygame.K_UP])) % len(self.map_options[self.language])
            if keys[pygame.K_RETURN] or keys[pygame.K_SPACE]:
                self.menu_input(self.state)
            if keys[pygame.K_BACKSPACE] and back_flag:
                self.open_index = 0

        elif self.state == 'level':
            self.main_menu = 'level menu'
            self.switch_index = (self.switch_index + int(keys[pygame.K_s]) + int(keys[pygame.K_DOWN]) - int (keys[pygame.K_w]) - int(keys[pygame.K_UP])) % len(self.level_options[self.language])
            if keys[pygame.K_RETURN] or keys[pygame.K_SPACE]:
                self.menu_input(self.state)
            elif keys[pygame.K_BACKSPACE] and back_flag:
                self.open_index = 0

        # sound
        if keys[pygame.K_RETURN] or keys[pygame.K_SPACE]:
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
        for i in range(len(self.level_options[self.language])):
            x = rect.centerx
            y = rect.top + rect.height / (10) + rect.height / 5 * i + v_offset
            color = COLORS['white'] if i == self.switch_index else COLORS['gray']
            name = self.level_options[self.language][i]


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
        for i in range(len(self.map_options[self.language])):
            x = rect.centerx
            y = rect.top + rect.height / (10) + rect.height / 5 * i + v_offset
            color = COLORS['white'] if i == self.switch_index else COLORS['gray']
            name = self.map_options[self.language][i]


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
        for i in range(len(SAVE_FILE_NAMES[self.language])):
            x = rect.centerx
            y = rect.top + rect.height / (10) + rect.height / 5 * i + v_offset
            color = COLORS['white'] if i == self.switch_index else COLORS['gray']
            name = SAVE_FILE_NAMES[self.language][i]


            text_surf = self.font.render(name, True, color)
            text_rect = text_surf.get_frect(center = (x,y))
            if rect.collidepoint(text_rect.center):
                self.display_surface.blit(text_surf, text_rect)
    
    def tablet_menu(self):
        # bg
        self.tablet_collected = sum(1 for key, value in self.save.file_info.items() if key.startswith('tablet_') and value)

        rect = pygame.FRect(0, 0, 300, 500)
        rect.center = (self.screen_dimension.width / 2 - 400, self.screen_dimension.height / 2)
        pygame.draw.rect(self.display_surface, COLORS['black'], rect, 0)
        pygame.draw.rect(self.display_surface, COLORS['gray'], rect, 5)

        # menu
        v_offset = 0 if self.switch_index < 5 else -(self.switch_index - 3) * rect.height / 5
        for i, name in enumerate(self.tablet_options):
            x = rect.centerx
            y = rect.top + rect.height / 10 + rect.height / 5 * i + v_offset
            color = COLORS['white'] if i == self.switch_index else COLORS['gray']

            text_surf = self.font.render(name, True, color)
            text_rect = text_surf.get_frect(center=(x, y))
            if rect.collidepoint(text_rect.center):
                self.display_surface.blit(text_surf, text_rect)

        # text part
        base_display = pygame.FRect(0, 0, 750, 500)
        base_display.center = (self.screen_dimension.width / 2 + 200, self.screen_dimension.height / 2)

        # check for height
        text = TEXT_TABLETS[self.language][self.switch_index]
        required_height = self.get_text_height_tablet(base_display, text)
        if required_height > base_display.height and self.switch_index < self.tablet_collected: # change needed
            base_display.height = required_height + 2 * TEXT_SETTINGS["padding_y"]
            base_display.center = (self.screen_dimension.width / 2 + 200, self.screen_dimension.height / 2)

        # draw
        pygame.draw.rect(self.display_surface, COLORS['black'], base_display, 0)
        pygame.draw.rect(self.display_surface, COLORS['gray'], base_display, 5)

        self.render_text_tablet(base_display)

    def hint_menu(self):
        stage = self.get_stage()
        base_display = pygame.FRect(0, 0, 400, 500)
        base_display.center = (self.screen_dimension.width / 2, self.screen_dimension.height / 2)

        # check for heigt
        text = TEXT_HINT[self.language][stage]
        required_height = self.get_text_height_hint(base_display, text)
        base_display.height = required_height + 2 * TEXT_SETTINGS["padding_y"]
        base_display.center = (self.screen_dimension.width / 2, self.screen_dimension.height / 2)

        # draw
        pygame.draw.rect(self.display_surface, COLORS['black'], base_display, 0)
        pygame.draw.rect(self.display_surface, COLORS['gray'],  base_display, 5)

        
        self.render_text_hint(base_display, stage)


        # old menu was for actions
        # bg
        #rect = pygame.FRect(0, 0 , 400, 500) # pos, x, y
        #rect.center = (self.screen_dimension.width / 2, self.screen_dimension.height / 2) # pos set to center screen
        #pygame.draw.rect(self.display_surface, COLORS['black'], rect, 0)
        #pygame.draw.rect(self.display_surface, COLORS['gray'], rect, 5)

        ## menu
        #v_offset = 0 if self.switch_index < 6 else -(self.switch_index - 3) * rect.height / 5
        #for i in range(len(self.action_options)):
        #    x = rect.centerx
        #    y = rect.top + rect.height / (10) + rect.height / 6 * i + v_offset
        #    color = COLORS['white']
        #    name = self.action_options[i]
        #    text_surf = self.font.render(name, True, color)
        #    text_rect = text_surf.get_frect(center = (x,y))
        #    if rect.collidepoint(text_rect.center):
        #        self.display_surface.blit(text_surf, text_rect)

    def options_menu(self):
        # bg
        rect = pygame.FRect(0, 0 , 400, 500) # pos, x, y
        rect.center = (self.screen_dimension.width / 2, self.screen_dimension.height / 2) # pos set to center screen
        pygame.draw.rect(self.display_surface, COLORS['black'], rect, 0)
        pygame.draw.rect(self.display_surface, COLORS['gray'], rect, 5)

        # menu
        v_offset = 0 if self.switch_index < 5 else -(self.switch_index - 3) * rect.height / 5 
        for i in range(len(self.setting_options[self.language])):
            x = rect.centerx
            y = rect.top + rect.height / (10) + rect.height / 5 * i + v_offset
            color = COLORS['white'] if i == self.switch_index else COLORS['gray']
            name = self.setting_options[self.language][i]


            text_surf = self.font.render(name, True, color)
            text_rect = text_surf.get_frect(center = (x,y))
            if rect.collidepoint(text_rect.center):
                self.display_surface.blit(text_surf, text_rect)

    def pause_info(self):
        #currentrly always called
        # bg
        rect = pygame.FRect(0, 0 , 100, 100) # pos, x, y
        rect.center = (self.screen_dimension.width / 2, (self.screen_dimension.height/2)-260) # pos set to center screen

        level_rect = pygame.FRect(0, 0 , 200, 70) # pos, x, y
        level_rect.center = (self.screen_dimension.width / 2, (self.screen_dimension.height / 2) - 300) # pos set to center screen
        pygame.draw.rect(self.display_surface, COLORS['black'], level_rect, 0)
        pygame.draw.rect(self.display_surface, COLORS['gray'], level_rect, 5)

        x = rect.centerx
        y = rect.top + rect.height / (10)
        color = COLORS['white']

        stage = self.get_stage()
        name = str(stage)
        #"current_file": "0"
        #f'level_{int(obj.properties['level'])}' in self.save.file_info:
        if stage == '': #will display the name of the safe file?
            pass
        else:
            name = f"Level {stage}"



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
        name = self.home_text[self.language]
        text_surf = self.font.render(name, True, color)
        text_rect = text_surf.get_frect(center = (x,y))
        if rect.collidepoint(text_rect.center):
            self.display_surface.blit(text_surf, text_rect)

    def map_info(self):
            # bg
        rect = pygame.FRect(0, 0 , 100, 200) # pos, x, y
        rect.center = (self.screen_dimension.width - 180, 120) # pos set to center screen

        # menu
        for i in range(len(self.map_text)): # work but only because its range is also 2
            x = rect.centerx
            y = rect.top + rect.height / (10) + rect.height / 5 * i
            color = COLORS['white']
            name = self.map_text[i][self.language]


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

    def ending_info(self, dt, ending_num):
        if ending_num == 1:
            ending_text = self.ending_text_1[self.language]
        else:
            ending_text = self.ending_text_2[self.language]

        # Font settings
        ending_font = pygame.font.Font(join(BASE_PATH, "data", "font_b.ttf"), 50)
        color = COLORS['white']

        # bg
        rect = pygame.FRect(0, 0, 1920, 1600)
        rect.center = (self.screen_dimension.width / 2, self.screen_dimension.height / 2)

        # draw
        for i, name in enumerate(ending_text):
            x = rect.centerx
            y = self.scrolling_text_y_positions[i]
            text_surf = ending_font.render(name, True, color)
            text_rect = text_surf.get_frect(center=(x, y))

            if rect.collidepoint(text_rect.center):
                self.display_surface.blit(text_surf, text_rect)

            self.scrolling_text_y_positions[i] += 100 * dt # initialized in main

    def level_tuto(self, level_num):
        # bg
        rect = pygame.FRect(0, 0 , 100, 200) # pos, x, y
        rect.center = (self.screen_dimension.width - 120, 160) # pos set to center screen

        # menu
        x = rect.centerx
        y = rect.top + rect.height / (10)
        color = COLORS['white']
        name = self.level_tuto_text[level_num][self.language]
        text_surf = self.font.render(name, True, color)
        text_rect = text_surf.get_frect(center = (x,y))
        if rect.collidepoint(text_rect.center):
            self.display_surface.blit(text_surf, text_rect)

    def render_text(self, display):
        font = pygame.font.Font(TEXT_SETTINGS["font_name"], TEXT_SETTINGS["font_size"])
        rect = display

        # Get text based on whether the tablet has been collected
        if self.switch_index < self.tablet_collected:
            text = TEXT_TABLETS[self.language][self.switch_index]
        else:
            #text = TEXT_TABLETS[self.language][self.switch_index]
            text_surface = font.render("???", True, TEXT_SETTINGS["text_color"])
            text_rect = text_surface.get_rect(center=rect.center)
            self.display_surface.blit(text_surface, text_rect)
            return  # Skip the rest of the function


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

    def render_text_tablet(self, display):
        font = pygame.font.Font(TEXT_SETTINGS["font_name"], TEXT_SETTINGS["font_size"])
        rect = display
        

        # Récupère le texte selon l’état de la tablette
        if self.switch_index < self.tablet_collected:
            text = TEXT_TABLETS[self.language][self.switch_index]
        else:
            text_surface = font.render("???", True, TEXT_SETTINGS["text_color"])
            text_rect = text_surface.get_rect(center=rect.center)
            self.display_surface.blit(text_surface, text_rect)
            return

        sentences = [s.strip() + '  ' for s in text.split('  ') if s.strip()]
        line_height = font.get_height() + TEXT_SETTINGS["line_spacing"]
        y = rect.y + TEXT_SETTINGS["padding_y"]

        for sentence in sentences:
            words = sentence.split()
            current_line = ""
            lines = []

            for word in words:
                test_line = current_line + word + " "
                if font.size(test_line)[0] < rect.width - (2 * TEXT_SETTINGS["padding_x"]):
                    current_line = test_line
                else:
                    lines.append(current_line)
                    current_line = word + " "
            lines.append(current_line)

            for line in lines:
                if y + line_height > rect.y + rect.height - TEXT_SETTINGS["padding_y"]:
                    return
                text_surface = font.render(line, True, TEXT_SETTINGS["text_color"])
                self.display_surface.blit(text_surface, (rect.x + TEXT_SETTINGS["padding_x"], y))
                y += line_height

            # Réduction du saut entre les phrases (divisé par 2)
            y += line_height // 2

    def render_text_hint(self, display, stage):
        font = pygame.font.Font(TEXT_SETTINGS["font_name"], TEXT_SETTINGS["font_size"])
        rect = display
    
        #stage = self.get_stage()
        text = TEXT_HINT[self.language][stage]
    
        sentences = [s.strip() + '  ' for s in text.split('  ') if s.strip()]
        line_height = font.get_height() + TEXT_SETTINGS["line_spacing"]
        y = rect.y + TEXT_SETTINGS["padding_y"]
    
        for sentence in sentences:
            words = sentence.split()
            current_line = ""
            lines = []
    
            for word in words:
                test_line = current_line + word + " "
                if font.size(test_line)[0] < rect.width - (2 * TEXT_SETTINGS["padding_x"]):
                    current_line = test_line
                else:
                    lines.append(current_line.rstrip())
                    current_line = word + " "
            lines.append(current_line.rstrip())
    
            for line in lines:
                if y + line_height > rect.y + rect.height - TEXT_SETTINGS["padding_y"]:
                    return
    
                text_surface = font.render(line, True, TEXT_SETTINGS["text_color"])
    
                # Zone disponible (avec padding)
                inner_left = rect.x + TEXT_SETTINGS["padding_x"]
                inner_width = rect.width - 2 * TEXT_SETTINGS["padding_x"]
    
                # x centré dans la zone inner
                x = inner_left + (inner_width - text_surface.get_width()) / 2
    
                self.display_surface.blit(text_surface, (x, y))
                y += line_height
    
            y += line_height // 2

    def get_text_height_tablet(self, rect, text):
        """Calcule la hauteur totale nécessaire pour afficher le texte."""
        font = pygame.font.Font(TEXT_SETTINGS["font_name"], TEXT_SETTINGS["font_size"])

        if self.switch_index < self.tablet_collected:
            text = TEXT_TABLETS[self.language][self.switch_index]
        else:
            return font.get_height()

        sentences = [s.strip() + '  ' for s in text.split('  ') if s.strip()]
        line_height = font.get_height() + TEXT_SETTINGS["line_spacing"]
        total_height = TEXT_SETTINGS["padding_y"]

        for sentence in sentences:
            words = sentence.split()
            current_line = ""
            lines = []

            for word in words:
                test_line = current_line + word + " "
                if font.size(test_line)[0] < rect.width - (2 * TEXT_SETTINGS["padding_x"]):
                    current_line = test_line
                else:
                    lines.append(current_line)
                    current_line = word + " "
            lines.append(current_line)

            total_height += len(lines) * line_height
            total_height += (line_height // 2) - (int(TEXT_SETTINGS["line_spacing"]) // 2) # adjustment for good space

        total_height += TEXT_SETTINGS["padding_y"]
        return total_height

    def get_text_height_hint(self, rect, text):
        """Calcule la hauteur totale nécessaire pour afficher le texte."""
        font = pygame.font.Font(TEXT_SETTINGS["font_name"], TEXT_SETTINGS["font_size"])


        sentences = [s.strip() + '  ' for s in text.split('  ') if s.strip()]
        line_height = font.get_height() + TEXT_SETTINGS["line_spacing"]
        total_height = TEXT_SETTINGS["padding_y"]

        for sentence in sentences:
            words = sentence.split()
            current_line = ""
            lines = []

            for word in words:
                test_line = current_line + word + " "
                if font.size(test_line)[0] < rect.width - (2 * TEXT_SETTINGS["padding_x"]):
                    current_line = test_line
                else:
                    lines.append(current_line)
                    current_line = word + " "
            lines.append(current_line)

            total_height += len(lines) * line_height
            total_height += (line_height // 2) - (int(TEXT_SETTINGS["line_spacing"]) // 2) # adjustment for good space

        total_height += TEXT_SETTINGS["padding_y"]
        return total_height

    def update(self):
        self.language = self.save.file_info['language']
        if self.open_index == 1:
            self.input()

    def draw(self):
        match self.state:
            case 'home' :
                self.home_menu()
            case 'map': 
                self.map_menu()
            case 'level': 
                self.level_menu()
                self.pause_info()
            case 'file': 
                self.file_menu()
            case 'tablet': 
                self.tablet_menu()
            case 'indice' : 
                self.hint_menu()
            case 'options': 
                self.options_menu()

