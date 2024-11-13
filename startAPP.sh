#!/bin/bash
cd /home/pi/Desktop
source env/bin/activate
cd /home/pi/Desktop/Athan-speaker-using-Raspberry-pi
pip install -r requirements.txt --quiet
sudo env "PATH=$PATH" python app.py
