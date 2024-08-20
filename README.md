# Athan-speaker-using-Raspberry-pi
Make an Athan alarm speaker that plays the athan audio at you local prayer times from mawaqit using a raspberry pi.

### Prerequisites: 
 -Raspberry pi with SD card and power supply
 -Speaker

Install raspberry pi OS and configure SSH:
 - On your computer, install Raspberry Pi Imager if you dont already have it from [here](https://www.raspberrypi.com/software/)
 - Open the imager, Choose your board, a Raspberry Pi OS (any os should work), and storage (the SD card you plugged in to your computer).
Press CRT+SHIFT+X to open customization menu: 
 - Set hostname and username and password. Make sure your username is pi or else the paths in the code wont work. (pi should be the default username)
 - Configure wireless LAN and enter your wifi name and password. Configure the rest of the settings.
 - In the services tab, enable SSH and click passwork authentication
 - Save the setting and click next, click yes to apply OS customization settings and **DON'T** format the disk if prompted

Either SSH into your Raspberry pi using the terminal on you computer using the command `ssh pi@raspberrypi.local`, (assuming your username is pi and hostname is raspberrypi, or you can replace the 'raspberrypi.local' with you pi's ip adress) or connect your pi to a monitor mouse and keyboard and open the terminal app.


### STEP 1:
Clone mawaqit-api directory from github:
- Open Desktop directory: `cd Desktop`
- Use the command: `git clone https://github.com/mrsofiane/mawaqit-api` to clone it.
- Navigate to directory: `cd mawaqit-api`
- Create virtual environment: `python -m  venv env` or `python3 -m  venv env`
- Activate the virtual environment `source env/bin/activate`
- Install dependencies using pip: `pip install -r requirements.txt` or `pip3 install -r requirements.txt`

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
```
nano Athans
```
```
nano FajrAthans
```
Go to the app.py file using the command `nano app.py` and change the path of ATHANS_DIR and FAJR_ATHANS_DIR to where you saved your athans. If you only have 1, still save it in a folder and select it from the Web interface later.





