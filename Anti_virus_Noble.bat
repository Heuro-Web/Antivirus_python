     @echo off
     echo Conversion en cours...
     pyinstaller --onefile --windowed --icon=virus.ico antivirus.py
     echo Conversion terminée. Le fichier .exe se trouve dans le dossier "dist".
     pause