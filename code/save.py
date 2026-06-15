from settings import *

import json
import os
import platform
from os.path import join
from datetime import datetime

class Save:
    def __init__(self, level_files):
        self.level_files = level_files
        save_dir = self._get_save_dir()
        self.save_path = join(save_dir, 'save_file_nebulon.json')
        self.backup_path = join(save_dir, 'save_file_backup_nebulon.json')

        self._default_info_template = {
            'language': 'fr',
            'grid': True,
            'shake': True,
            'icon_pos': '[576, 704]',
            'level_1': False
        }

        # 1) Try to load JSON
        try:
            with open(self.save_path, encoding='utf-8') as f:
                self.info = json.load(f)

        except Exception:
            # Build a full clean base and write it once
            clean = {'current_file': SAVE_FILES[0]}
            for key in SAVE_FILES:
                clean[key] = self._new_slot()
            self.info = clean
            self.save_to_disk()  # single, explicit write of the blank save

        # Normalize in-memory; persist if anything was back-filled
        if self._normalize_structure():
            self.save_to_disk()
        self.update()

    # public
    def update(self):
        cur = self.info.get('current_file', SAVE_FILES[0])
        if cur not in SAVE_FILES:
            cur = SAVE_FILES[0]
            self.info['current_file'] = cur

        self._ensure_slot_exists(cur, persist=False)  # avoid unexpected write here
        self.current_file = cur
        self.file_info = self.info[cur]

    def save_to_disk(self):
        backup_path = self.backup_path

        # Guide to tell how to recover the file
        #header = f'# Largest non-corrupted save file was saved {datetime.now().isoformat(timespec="seconds")}\nTo load that file put the following content inside save_file.txt:\n'
        # Get the JSON-only size of the backup (strip header so comparison is fair)
        backup_json_size = 0
        if os.path.exists(backup_path):
            with open(backup_path, 'r', encoding='utf-8') as f:
                first_line = f.readline()
                rest = f.read() if first_line.startswith('Biggest') else first_line + f.read()
            backup_json_size = len(rest.encode('utf-8'))

        # Only overwrite backup if the current save is at least as large — prevents a
        # fresh/blank save (created after corruption) from replacing a progressed backup
        if os.path.exists(self.save_path) and os.path.getsize(self.save_path) >= backup_json_size:
            with open(self.save_path, 'r', encoding='utf-8') as f:
                current_content = f.read()
            with open(backup_path, 'w', encoding='utf-8') as f:
                #f.write(header)
                f.write(current_content)

        with open(self.save_path, 'w', encoding='utf-8') as f:
            json.dump(self.info, f, indent=4)

    # INTERNAL
    @staticmethod
    def _get_save_dir():
        system = platform.system()
        if system == 'Windows':
            base = os.environ.get('APPDATA', os.path.expanduser('~'))
        elif system == 'Darwin':
            base = os.path.expanduser('~/Library/Application Support')
        else:
            base = os.environ.get('XDG_DATA_HOME', os.path.expanduser('~/.local/share'))
        path = os.path.join(base, 'Nebulon')
        os.makedirs(path, exist_ok=True)
        return path

    def _new_slot(self):
        return self._default_info_template.copy()

    def _ensure_slot_exists(self, slot_key, persist=True):
        if slot_key not in self.info or not isinstance(self.info[slot_key], dict):
            self.info[slot_key] = self._new_slot()
            if persist:
                self.save_to_disk()

    def _normalize_structure(self):
        changed = False
        if self.info.get('current_file') not in SAVE_FILES:
            self.info['current_file'] = SAVE_FILES[0]
            changed = True
        for key in SAVE_FILES:
            if key not in self.info or not isinstance(self.info[key], dict):
                self.info[key] = self._new_slot()
                changed = True
            else:
                # Fill in any keys added to the template that old saves are missing
                for k, v in self._default_info_template.items():
                    if k not in self.info[key]:
                        self.info[key][k] = v
                        changed = True
        return changed
