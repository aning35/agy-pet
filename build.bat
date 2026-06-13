@echo off
echo Building AgyPet...
.\venv\Scripts\pyinstaller.exe --clean --noconfirm --onefile --windowed --add-data "assets/sounds;assets/sounds" --add-data "assets/gifs;assets/gifs" --name AgyPet src\app.py
echo Build complete! The executable is located in the dist folder.
