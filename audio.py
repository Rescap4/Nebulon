from settings import *
from support import *

class AudioManager:
    def __init__(self):
        pygame.mixer.set_num_channels(5)
        self.music_folder = 'sounds'
        self.current_music_key = None
        self.channels = {
            'music': pygame.mixer.Channel(0),
            'looped': pygame.mixer.Channel(1),
            'sfx_1': pygame.mixer.Channel(2),
            'sfx_2': pygame.mixer.Channel(3),
            'sfx_3': pygame.mixer.Channel(4)
        }

        self.sfx_channels = [self.channels['sfx_1'], self.channels['sfx_2'], self.channels['sfx_3']]
        self.audio_files = audio_importer('sounds')  # Dict of {key: pygame.mixer.Sound}

        # Default volumes
        self.default_volumes = {
            'music': 1.0,
            'looped': 1.0,
            'sfx': 1.0
        }

        self.muted = {
            'music': False,
            'looped': False,
            'sfx': False
        }


    def play_sfx(self, key, volume=1.0):
        if key not in self.audio_files:
            print(f"[AudioManager] Sound '{key}' not found.")
            return
        if self.muted['sfx']:
            return

        sound = self.audio_files[key]
        sound.set_volume(volume)

        for channel in self.sfx_channels:
            if not channel.get_busy():
                channel.play(sound)
                return

        # All busy, force playback
        self.sfx_channels[0].play(sound)


    def play_music(self, key, volume=1.0, loops=-1):
        if self.current_music_key == key:
            return  # Already playing this music
        if self.muted['music']:
            return

        music_file = join(self.music_folder, f"{key}.ogg")  # Adjust extension if needed

        if not os.path.exists(music_file):
            print(f"[AudioManager] Music file not found: {music_file}")
            return

        # Load and play the music
        pygame.mixer.music.load(music_file)
        pygame.mixer.music.set_volume(volume)
        pygame.mixer.music.play(loops)
        self.current_music_key = key

    def play_loop(self, key, volume=1.0):
        if key in self.audio_files:
            self.default_volumes['looped'] = volume
            if self.muted['looped']:
                return
            sound = self.audio_files[key]
            sound.set_volume(volume)
            self.channels['looped'].play(sound, loops=-1)
        else:
            print(f"[AudioManager] Looped sound '{key}' not found.")

    def stop_loop(self):
        self.channels['looped'].stop()

    def stop_all(self):
        for channel in self.channels.values():
            channel.stop()

    # ---------- MUTE/UNMUTE FUNCTIONS ----------

    def mute_music(self):
        self.muted['music'] = True
        pygame.mixer.music.stop()
        self.channels['music'].set_volume(0)

    def unmute_music(self): # demo, it doesnt restart the music by itself
        self.muted['music'] = False
        self.channels['music'].set_volume(self.default_volumes['music'])

    def mute_looped(self):
        self.muted['looped'] = True
        self.channels['looped'].set_volume(0)

    def unmute_looped(self):
        self.muted['looped'] = False
        self.channels['looped'].set_volume(self.default_volumes['looped'])

    def mute_sfx(self):
        self.muted['sfx'] = True
        for channel in self.sfx_channels:
            channel.set_volume(0)

    def unmute_sfx(self):
        self.muted['sfx'] = False
        for channel in self.sfx_channels:
            channel.set_volume(self.default_volumes['sfx'])
