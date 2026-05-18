from settings import *
import os

# BASE_PATH est maintenant défini dans settings.py

def import_image(*path, format='png', alpha=True):
    full_path = os.path.join(BASE_PATH, *path) + f'.{format}'
    return pygame.image.load(full_path).convert_alpha() if alpha else pygame.image.load(full_path).convert()

def import_folder(*path):
    frames = []
    full_folder_path = os.path.join(BASE_PATH, *path)
    for folder_path, _, file_names in os.walk(full_folder_path):
        for file_name in sorted(file_names, key=lambda name: int(name.split('.')[0])):
            full_path = os.path.join(folder_path, file_name)
            frames.append(pygame.image.load(full_path).convert_alpha())
    return frames

def audio_importer(*path):
    sfx_sounds = {}
    full_folder_path = os.path.join(BASE_PATH, *path)
    for folder_path, _, file_names in os.walk(full_folder_path):
        for file_name in file_names:
            key = file_name.rsplit('.', 1)[0]
            full_path = os.path.join(folder_path, file_name)
            if 'music' not in key.lower():
                sfx_sounds[key] = pygame.mixer.Sound(full_path)
    return sfx_sounds
