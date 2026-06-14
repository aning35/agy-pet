@echo off
echo Building AgyPet...

set PYINSTALLER_CMD=pyinstaller.exe
if exist .\venv\Scripts\pyinstaller.exe (
    set PYINSTALLER_CMD=.\venv\Scripts\pyinstaller.exe
) else (
    python -c "import PyInstaller" 2>nul
    if %errorlevel% equ 0 (
        set PYINSTALLER_CMD=python -m PyInstaller
    ) else (
        echo Error: PyInstaller is not installed in the active Python environment or .\venv.
        exit /b 1
    )
)

echo Using: %PYINSTALLER_CMD%
%PYINSTALLER_CMD% --clean --noconfirm --onefile --windowed --add-data "assets/sounds;assets/sounds" --add-data "assets/gifs;assets/gifs" --add-data "assets/tray_icon.png;assets" --icon="assets/icon.ico" --name AgyPet src\app.py

echo Build complete! The executable is located in the dist folder.

