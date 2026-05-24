# Additional information about the game structure

## Save file and backup

The game save it's progress in save_file.txt, it is important that this file is not moved from it's folder.

The largest non-corrupted save file is stored in **save_file_backup.txt**
To load the backup, rename the file as **save_file.txt** and replace the newly created save



## Final distribution

```
Nebulon_Game/
├── Nebulon.exe       (everything is included)
└── data/             (created automatically for save files)
    ├── save_file.txt
    └── save_file_backup.txt
```

**Compress `Nebulon_Game/` into a ZIP to share**

---

##  How BASE_PATH works

```python
# settings.py
import sys
import os

if getattr(sys, 'frozen', False):
    # Exe mode: resources extracted temporarily
    BASE_PATH = sys._MEIPASS  # e.g. C:\Users\...\Temp\_MEI123456
else:
    # Development mode
    BASE_PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    # e.g. C:\Users\...\Nebulon
```

**Result:**
- In **development**: `BASE_PATH = "C:\...\Nebulon"`
- In **exe**: `BASE_PATH = "C:\Users\...\Temp\_MEI123456"`

All resource paths now use `BASE_PATH`

---
