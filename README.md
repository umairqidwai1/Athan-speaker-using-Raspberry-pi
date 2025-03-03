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

### IMPORTANT:
For Rasberry pi lite os, Don't forget to make a file called Desktop using the command `mkdir Desktop`, since all the files have to be in that folder for the code to work.

The regular version of rasbian should already include the Desktop folder and these packages by default.

### STEP 1:
Create and activate virual env:
```
cd /home/pi/Desktop
python -m  venv env
source env/bin/activate
```
Update and Install packages:
```
sudo apt-get update -y
sudo apt install -y git
sudo apt install -y python3-pip
sudo apt install -y ffmpeg
sudo apt install -y libsdl2-mixer-2.0-0
sudo apt install -y libsdl2-mixer-dev
```
### STEP 2:
Clone mawaqit-api directory from github:

```
cd /home/pi/Desktop
git clone https://github.com/mrsofiane/mawaqit-api
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
sudo apt-get install redis -y
```
Set the environment variables for Redis host and port using the commands:
```
export REDIS_URI=redis://localhost:6379
export USE_REDIS=true
```


### STEP 3:

Clone this repository. Copy the link from the top and run the command: 
```
cd /home/pi/Desktop
git clone https://github.com/umairqidwai1/Athan-speaker-using-Raspberry-pi.git
```


### STEP 4:
Make the startAPI.sh file executable
```
cd /home/pi/Desktop/Athan-speaker-using-Raspberry-pi
chmod +x startAPI.sh
chmod +x startAPP.sh
chmod +x auto_pull.sh
```
Run the command:
```
crontab -e
```
and select the first editor by typing 1.

At the bottom of the file add these lines:
```
XDG_RUNTIME_DIR=/run/user/1000
@reboot /home/pi/Desktop/Athan-speaker-using-Raspberry-pi/startAPI.sh
@reboot /home/pi/Desktop/Athan-speaker-using-Raspberry-pi/startAPP.sh
* * * * * /bin/bash /home/pi/Desktop/Athan-speaker-using-Raspberry-pi/auto_pull.sh
0 3 * * * sudo reboot
```

Reboot your Pi using the command: 
```
sudo reboot
```

When the Pi is up again, everything should work. You can change some setting using the local website. Go to  http://your_raspberry_pi_ip_adress:5000

Install comitup
```
wget https://davesteele.github.io/comitup/deb/davesteele-comitup-apt-source_1.2_all.deb
dpkg -i --force-all davesteele-comitup-apt-source_1.2_all.deb
rm davesteele-comitup-apt-source_1.2_all.deb
apt-get update
apt-get install comitup comitup-watch
rm /etc/network/interfaces
systemctl mask dnsmasq.service
systemctl mask systemd-resolved.service
systemctl mask dhcpd.service
systemctl mask dhcpcd.service
systemctl mask wpa-supplicant.service
systemctl enable NetworkManager.service
```
