# Athan-speaker-using-Raspberry-pi
Make an Athan alarm speaker that plays the athan audio at you local prayer times.

###Prerequisites: 
 -Raspberry pi with imaged SD card and power supply
 -Speaker

### STEP 1:
Clone mawaqit-api directory from github. Follow the instruction [here](https://mrsofiane.me/mawaqit-api/#/docs/installation)

Install redis using the commands:
```
sudo apt-get update
sudo apt-get install redis
```
Set the environment variables for Redis host and port using the commands:
```
export REDIS_URI=redis://localhost:6379/0
export USE_REDIS=true
```

### STEP 2:
Clone this repository. Copy the link from the top and run the command: 
  `git clone` [link to this repo]

### STEP 3:
Create a folder called Athans and one called FajrAthans and save all your .wav athan audio files there.
run the commands:
`nano Athans`
`nano FajrAthans`

Go to the app.py file using the command `nano app.py` and change the path of ATHANS_DIR and FAJR_ATHANS_DIR to where you saved your athans. If you only have 1, still save it in a folder and select it from the Web interface later.


