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
Remeber, if you have the light version, make a file called Desktop using the command `sudo mkdir Desktop`, since all the files have to in that folder for the code to work.
```
cd /home/pi/Desktop
git clone https://github.com/mrsofiane/mawaqit-api
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
cd mawaqit-api
```
Install dependencies using pip:
```
pip install -r requirements.txt
```
or 
```
pip3 install -r requirements.txt
```
Install redis using the commands:
```
sudo apt-get update
sudo apt-get install redis
pip install schedule
```
Set the environment variables for Redis host and port using the commands:
```
export REDIS_URI=redis://localhost:6379
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
@reboot /home/pi/Desktop/startAPI.sh
@reboot /usr/bin/python3 /home/pi/Desktop/monitor.py >> /home/pi/Desktop/monitor.log 2>&1
0 * * * * /usr/bin/python3 /home/pi/Desktop/monitor.py >> /home/pi/Desktop/monitor.log 2>&1
```


### STEP 4:
Make 2 folder, one for Fajr athan audio files and one for Regular athan audio files:
```
cd /home/pi/Desktop
mkdir Athans
mkdir FajrAthans
```
Add all you Athan Audio Files to thier corresponding folders.

Make SURE to create these folders since the path in the code points to them. Even if you only have one audio file to input in each, **STILL MAKE THE FOLDERS**.


Everything should work now. You can change some setting using the local website. Go to  http://your_raspberry_pi_ip_adress:5000


### Adding Athan Audio files:

You can only add .mp3 or .wav audio files. There are 3 ways to add Athan audio to your raspberry pi:

1: Go to the webpage listed above and click on the add button, then select you audio file

2: Manually add the files by downloading then on you raspberry pi and moving them to the Athans for FajrAthans Directories.

3: If you already have the audio files on you computer, open terminal and navigate to the folder where the file is saved. Enter the command 
```
scp file_name pi@your_pi_hostname:/home/pi/Desktop/Athans
```
change the last file to FajrAthans if the file is a Fajr Athan.

### Changing IP adress to static:

You IP adress will change every so often, so if you don't want the hastle of having to find you PI's new ip adress all the time, you can set a static one:

Enter this into you terminal:
```
sudo nano /etc/resolv.conf
```

Copy and paste this code at the bottom:
```
interface NETWORK 
static ip_address=STATIC_IP/24
static routers=ROUTER_IP 
static domain_name_servers=DNS_IP
```

Replace these names as follows:

NETWORK – your network connection type: eth0 (Ethernet) or wlan0 (wireless).
STATIC_IP – the static IP address you want to set for the Raspberry Pi.
ROUTER_IP – the gateway IP address for your router on the local network.
DNS_IP – the DNS IP address (typically the same as your router’s gateway address).

Here is an example:
```
interface wlan0
static ip_address=10.0.0.28/24
static routers=10.0.0.1
static domain_name_servers=10.0.0.1
```

Reboot your raspberry pi:
```
sudo reboot
```
