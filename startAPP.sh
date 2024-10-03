#!/bin/bash
cd /home/pi/Desktop
source env/bin/activate
cd Athan-speaker-using-Raspberry-pi
sudo env "PATH=$PATH" python app.py 
