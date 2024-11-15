#!/bin/bash
cd /home/pi/Desktop
source env/bin/activate
cd /home/pi/Desktop/Athan-speaker-using-Raspberry-pi
pip3 install -r requirements.txt
sudo env "PATH=$PATH" python app.py
