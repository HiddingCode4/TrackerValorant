@echo off
cd /d "%~dp0"
py -3 -m venv .venv
if errorlevel 1 goto fail
.venv\Scripts\python -m pip install pyinstaller==6.16.0
if errorlevel 1 goto fail
.venv\Scripts\python -m PyInstaller --noconfirm --clean --onefile --windowed --name Hidding --icon assets/hidding.ico --add-data "assets;assets" --add-data "demo.json;." app.py
if errorlevel 1 goto fail
echo Hidding.exe disponible dans dist
pause
exit /b 0
:fail
echo Compilation echouee. Installer Python 3.12 et verifier la connexion Internet.
pause
exit /b 1
