rm -rf build
rm -rf dist
pip install --upgrade pip
pip3 install pyinstaller
pip3 install --upgrade PyInstaller pyinstaller-hooks-contrib
pip3 install -r requirements.txt --force-reinstall
pyinstaller --name="mrgit" --windowed --exclude-module _bootlocale --onefile main.py --noupx --hidden-import=_cffi_backend
cp dist/mgit ~/.local/bin/mgit
chmod a+x ~/.local/bin/mgit
