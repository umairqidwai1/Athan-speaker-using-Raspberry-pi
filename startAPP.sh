#!/bin/bash
cd /home/pi/Desktop/Athan-speaker-using-Raspberry-pi
source /home/pi/Desktop/env/bin/activate
pip install -r requirements.txt
sudo /home/pi/Desktop/env/bin/python app.py
