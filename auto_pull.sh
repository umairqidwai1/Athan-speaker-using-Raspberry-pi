#!/bin/bash
cd /home/pi/Desktop/Athan-speaker-using-Raspberry-pi
git fetch origin test3
LOCAL=$(git rev-parse HEAD)
REMOTE=$(git rev-parse origin/main)

if [ $LOCAL != $REMOTE ]; then
    echo "New changes detected. Pulling latest code..."
    git pull origin test3
else
    echo "No changes."
fi
