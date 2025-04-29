from settings import *

class Save:
    def __init__(self, level_files):
        self.level_files = level_files
        #self.current_file = 'Alpha' # default but is changed when another save should be loaded
        default_info = {'grid': False, 'shake': True, 'icon_pos': '[512, 704]', 'level_1': False}

        try:
            with open(join('data', 'save_file.txt')) as save_file:
                self.info = json.load(save_file)
            #print('file loaded')        
        except: # default
            self.current_file = 'Alpha'
            self.info = {
                'current_file' : SAVE_FILES[0],
                SAVE_FILES[0]: default_info.copy(),
                SAVE_FILES[1]: default_info.copy(),
                SAVE_FILES[2]: default_info.copy(),
                SAVE_FILES[3]: default_info.copy(),
                SAVE_FILES[4]: default_info.copy()
            }

    def update(self):
        # maybe not optimal but wtv
        # should be called only when exiting lvl
        self.current_file = self.info['current_file']
        self.file_info = self.info[self.current_file]

