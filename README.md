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
```
cd Desktop
git clone https://github.com/mrsofiane/mawaqit-api` to clone it.
cd mawaqit-api
```
Create virtual environment:
```
python -m  venv env
```
or
```
python3 -m  venv env
```
Activate Virtual enviroment:
```
source env/bin/activate
```
Install dependencies using pip:
```
pip install -r requirements.txt`
```
or 
```
pip3 install -r requirements.txt
```
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
```
cd /home/pi/Desktop
git clone https://github.com/umairqidwai1/Athan-speaker-using-Raspberry-pi.git
```


### STEP 3:
Make the startAPI.sh file executable
```
cd /home/pi/Desktop/Athan-speaker-using-Raspberry-pi
chmod +x startAPI.sh
```
Run the command:
```
crontab -e
```
and select the first editor by typing 1.

At the top of the file add the line:
```
XDG_RUNTIME_DIR=/run/user/1000
```
At the bottom of the file add these lines:
```
@reboot /home/umair/Desktop/startAPI.sh
@reboot /usr/bin/python3 /home/umair/Desktop/monitor.py >> /home/umair/Desktop/monitor.log 2>&1
0 * * * * /usr/bin/python3 /home/umair/Desktop/monitor.py >> /home/umair/Desktop/monitor.log 2>&1
```


### STEP 4:
Make 2 folder, one for Fajr athan audio files and one for Regular athan audio files:
```
cd /home/pi/Desktop
mkdir Athans
mkdir FajrAthans
```
Add all you Athan Audio Files to thier corresponding folders.

Make SURE to create these folders since the paths in the code point to them. Even if you only have one audio file to input in each, **STILL MAKE THE FOLDERS**.
