@echo off
rem Builds a Windows version of the game that runs without Python installed.
rem Run this on a Windows computer, from this folder:  build.bat
python -m pip install pyinstaller
python -m PyInstaller --noconfirm --onedir --noconsole --name ClashOfSorcerers --add-data "web;web" play.py
echo.
echo Done. Zip the folder  dist\ClashOfSorcerers  and share it. Players run ClashOfSorcerers.exe inside it.
pause
