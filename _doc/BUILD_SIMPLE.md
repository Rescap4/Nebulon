#  Build Nebulon - Méthode simple

##  Modifications effectuées

Code modifié pour qu'il fonctionne avec PyInstaller `--onefile` :

### Fichiers modifiés :

1. **[code/support.py](code/support.py)**
   - Ajout de `BASE_PATH` qui détecte si on est en mode exe ou développement
   - Les fonctions `import_image()`, `import_folder()`, `audio_importer()` utilisent maintenant `BASE_PATH`

2. **[code/main.py](code/main.py)**
   - Les chemins TMX utilisent `BASE_PATH`
   - La fonction `get_level_files()` utilise `BASE_PATH`

3. **[code/save.py](code/save.py)**
   - Le fichier de sauvegarde reste dans le répertoire courant (à côté de l'exe)
   - Création automatique du dossier `data/` si nécessaire

##  Comment ça marche

### En mode développement :
```
Nebulon/
├── code/main.py
├── data/          ← Lecture depuis ici
├── images/        ← Lecture depuis ici
└── sounds/        ← Lecture depuis ici
```

### En mode exe :
```
Nebulon_Game/
├── Nebulon.exe                    ← Contient data, images, sounds extraits dans _MEIPASS
└── data/
    └── save_file.txt              ← Sauvegarde créée ici
```

PyInstaller extrait temporairement les ressources dans `C:\Users\...\Temp\_MEI123456\`, mais le code utilise automatiquement `sys._MEIPASS` pour les trouver.

##  Créer l'exe

### Méthode 1 : Script automatique

```powershell
.\build_simple.bat
```

### Méthode 2 : Ligne de commande

```powershell
pyinstaller --onefile --add-data "data;data" --add-data "images;images" --add-data "sounds;sounds" --noconsole --name=Nebulon code/main.py
```

## Résultat

Après le build :

```
Nebulon_Game/
├── Nebulon.exe       (~100-150 MB - tout est dedans !)
└── data/             (dossier pour les sauvegardes)
```

**Avantages de cette méthode :**
- Un seul fichier `.exe` (tout est inclus)
- Les sauvegardes sont créées à côté de l'exe
- Facile à distribuer (juste le dossier `Nebulon_Game/`)
- Pas besoin de .spec compliqué

##  Tester

```powershell
cd Nebulon_Game
.\Nebulon.exe
```

Le jeu devrait :
- Se lancer sans erreur
- Charger tous les graphismes
- Jouer la musique
- Créer `data/save_file.txt` automatiquement

### BASE_PATH dans support.py

```python
if getattr(sys, 'frozen', False):
    # Mode exe : PyInstaller
    BASE_PATH = sys._MEIPASS
else:
    # Mode développement
    BASE_PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
```

**Résultat :**
- En développement : `BASE_PATH = "C:\...\Nebulon"`
- En exe : `BASE_PATH = "C:\Users\...\Temp\_MEI123456"`

### Sauvegarde dans le répertoire courant

```python
# save.py
self.save_path = join('data', 'save_file.txt')  # Relatif au répertoire courant
os.makedirs('data', exist_ok=True)              # Créer data/ si nécessaire
```

**Résultat :**
- Le fichier de sauvegarde est créé à `Nebulon_Game/data/save_file.txt`
- Pas dans le dossier temporaire de PyInstaller !

##  Important

### Ressources (data, images, sounds)
- Lecture depuis `sys._MEIPASS` (dossier temporaire)
- Incluses dans l'exe via `--add-data`

### Sauvegardes (data/save_file.txt)
- Écriture dans le répertoire courant (à côté de l'exe)
- Persiste entre les sessions

## Dépannage

### L'exe ne se lance pas
1. Vérifiez que pygame-ce est installé : `pip install pygame-ce`
2. Rebuildez avec `build_simple.bat`

### Erreur "file not found"
- Les ressources sont bien incluses dans l'exe
- Vérifiez que le build s'est terminé sans erreur

### Les sauvegardes ne persistent pas
- Vérifiez que le dossier `data/` existe à côté de l'exe
- Le script `build_simple.bat` le crée automatiquement

## Commande complète expliquée

```bash
pyinstaller \
  --onefile                          # Un seul fichier exe
  --add-data "data;data"             # Inclure data/ dans l'exe
  --add-data "images;images"         # Inclure images/ dans l'exe
  --add-data "sounds;sounds"         # Inclure sounds/ dans l'exe
  --noconsole                        # Pas de fenêtre console
  --name=Nebulon                     # Nom de l'exe
  code/main.py                       # Script principal
```

---

**Pour builder :** `.\build_simple.bat`

**Pour tester :** `Nebulon_Game\Nebulon.exe`
