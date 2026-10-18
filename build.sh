#!/bin/sh
# Builds a Mac or Linux version of the game that runs without Python installed.
# Run this on the same kind of computer you are building for:  sh build.sh
python3 -m pip install pyinstaller
python3 -m PyInstaller --noconfirm --onedir --noconsole --name ClashOfSorcerers --add-data "web:web" play.py
echo
echo "Done. Zip the folder  dist/ClashOfSorcerers  and share it."
