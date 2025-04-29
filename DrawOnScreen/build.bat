@echo off
echo Installing required packages...
pip install -r requirements.txt
pip install pyinstaller
pip install Pillow

echo Building application...
pyinstaller --clean --noconfirm --icon=app_icon.ico --noconsole --onefile paint_app.py

echo Done!
echo The executable can be found in the 'dist' folder.
pause 