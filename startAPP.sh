#!/bin/bash
cd /home/pi/Desktop
source env/bin/activate
cd Athan-speaker-using-Raspberry-pi
git pull origin main
sudo env "PATH=$PATH" python app.py 
