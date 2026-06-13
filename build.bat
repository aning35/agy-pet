@echo off
echo Building AgyPet...
.\venv\Scripts\pyinstaller.exe --clean --noconfirm --onefile --windowed --add-data "assets/sounds;assets/sounds" --add-data "assets/gifs;assets/gifs" --add-data "assets/tray_icon.png;assets" --icon="assets/icon.ico" --name AgyPet src\app.py
echo Build complete! The executable is located in the dist folder.
