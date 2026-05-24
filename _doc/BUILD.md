#  Build Nebulon

##  Create the executable

### Method 1: Automatic script

```powershell
.\build.bat
```

### Method 2: Command line

```powershell
pyinstaller --onefile --add-data "data;data" --add-data "images;images" --add-data "sounds;sounds" --noconsole --name=Nebulon code/main.py
```

## Result

After the build:

```
Nebulon_Game/
├── Nebulon.exe
└── data/             (folder for save files)
```

##  Play

```powershell
cd Nebulon_Game
.\Nebulon.exe
```
