#!/bin/bash
cd /home/pi/Desktop
source env/bin/activate
cd /home/pi/Desktop/Athan-speaker-using-Raspberry-pi
pip install flask_socketio
pip install schedule
pip install yt-dlp
pip install pygame
pip install psutil
pip install flask
pip install pydub
pip install evdev
sudo env "PATH=$PATH" python app.py
