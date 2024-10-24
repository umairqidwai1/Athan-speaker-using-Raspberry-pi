#!/bin/bash
cd /home/pi/Desktop
source env/bin/activate
cd /home/pi/Desktop/Athan-speaker-using-Raspberry-pi
sudo env "PATH=$PATH" python monitor.py
