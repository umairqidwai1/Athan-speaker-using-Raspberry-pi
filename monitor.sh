#!/bin/bash
cd /home/pi/Desktop/Athan-speaker-using-Raspberry-pi
sudo /home/pi/Desktop/env/bin/python monitor.py >> /home/pi/Desktop/monitor.log 2>&1 &
