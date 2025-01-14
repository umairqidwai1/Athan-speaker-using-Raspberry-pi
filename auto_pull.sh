#!/bin/bash
cd /home/pi/Desktop/Athan-speaker-using-Raspberry-pi
git fetch origin main
LOCAL=$(git rev-parse HEAD)
REMOTE=$(git rev-parse origin/main)

if [ $LOCAL != $REMOTE ]; then
    echo "New changes detected. Pulling latest code..."
    git pull origin main
else
    echo "No changes."
fi
