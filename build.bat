@echo off
chcp 65001 >nul
echo ══════════════════════════════════════════
echo   Build Nebulon avec PyInstaller
echo ══════════════════════════════════════════
echo.

:: Nettoyer les anciens builds
echo [1/3] Nettoyage...
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist
echo       ✓ Nettoyage terminé

echo.
echo [2/3] Création de l'exe...
echo       (Cela peut prendre 1-2 minutes)

pyinstaller --onefile --add-data "data;data" --add-data "images;images" --add-data "sounds;sounds" --noconsole --name=Nebulon code/main.py

if errorlevel 1 (
    echo.
    echo ✗ Erreur lors du build
    pause
    exit /b 1
)

echo       ✓ Build terminé

echo.
echo [3/3] Préparation...

:: Créer le dossier de distribution
if not exist "Nebulon_Game" mkdir "Nebulon_Game"

:: Copier l'exe
copy "dist\Nebulon.exe" "Nebulon_Game\" >nul

:: Créer le dossier data (pour les sauvegardes)
if not exist "Nebulon_Game\data" mkdir "Nebulon_Game\data"

:: Copier les ressources (déjà dans l'exe, mais on copie data pour les sauvegardes)
echo       ✓ Package créé

echo.
echo ══════════════════════════════════════════
echo   BUILD RÉUSSI !
echo ══════════════════════════════════════════
echo.
echo L'exe est dans : Nebulon_Game\Nebulon.exe
echo.
echo Structure finale :
echo   Nebulon_Game\
echo   ├── Nebulon.exe  (contient data, images, sounds)
echo   └── data\        (créé pour les sauvegardes)
echo.
echo Note : Les sauvegardes seront créées dans
echo        Nebulon_Game\data\save_file.txt
echo.

pause
