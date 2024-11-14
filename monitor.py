import os
import time
import psutil
import subprocess
import datetime

# Function to check if app.py is running
def is_app_running():
    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
        # Ensure cmdline is not None before checking for 'app.py'
        if proc.info['cmdline'] and 'app.py' in proc.info['cmdline']:
            return True
    return False


# Function to reboot the Raspberry Pi at 1am once a week
def schedule_reboot():
    current_time = datetime.datetime.now()
    reboot_time = current_time.replace(hour=1, minute=0, second=0, microsecond=0)
    # Check if today is the reboot day (e.g., Sunday)
    if current_time.weekday() == 6 and current_time >= reboot_time:
        print("Rebooting the system...")
        subprocess.run(['sudo', 'reboot'])
        
# Monitor loop
while True:
    if is_app_running():
        print("app.py is running.")
    else:
        print("app.py is not running! Restarting the system...")
        subprocess.run(['sudo', 'reboot'])
    
    # Check every second
    time.sleep(1)

    # Schedule weekly reboot
    schedule_reboot()
