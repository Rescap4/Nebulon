from settings import *

import json
import os
from os.path import join
from pathlib import Path
from datetime import datetime

class Save:
    def __init__(self, level_files):
        self.level_files = level_files
        # Le fichier de sauvegarde est créé à côté de l'exe (répertoire de travail)
        # Pas dans le dossier temporaire de PyInstaller
        self.save_path = join('data', 'save_file.txt')
        # Créer le dossier data s'il n'existe pas
        os.makedirs('data', exist_ok=True)

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

        except Exception as e:
            # 2) Archive raw original BEFORE any write
            p = Path(self.save_path)
            try:
                raw = p.read_text(encoding='utf-8', errors='replace') if p.exists() else '<missing file>'
            except Exception:
                raw = '<file unreadable>'

            with open(join('data', 'save_file_backup.txt'), 'a', encoding='utf-8') as archive:
                archive.write(f"\n--- {datetime.now().isoformat(timespec='seconds')} ---\n")
                archive.write(f"Error: {repr(e)}\n")
                archive.write(raw + "\n")

            # 3) Build a full clean base and write it once
            clean = {'current_file': SAVE_FILES[0]}
            for key in SAVE_FILES:
                clean[key] = self._new_slot()
            self.info = clean
            self.save_to_disk()  # single, explicit write of the blank save

        # 4) Normalize in-memory; persist if anything was back-filled
        if self._normalize_structure():
            self.save_to_disk()
        self.update()

    # ---------- PUBLIC ----------
    def update(self):
        cur = self.info.get('current_file', SAVE_FILES[0])
        if cur not in SAVE_FILES:
            cur = SAVE_FILES[0]
            self.info['current_file'] = cur

        self._ensure_slot_exists(cur, persist=False)  # avoid unexpected write here
        self.current_file = cur
        self.file_info = self.info[cur]

    def save_to_disk(self):
        with open(self.save_path, 'w', encoding='utf-8') as f:
            json.dump(self.info, f, indent=4)

    # ---------- INTERNAL ----------
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
