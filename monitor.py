import os
import socket
import subprocess
import time
time.sleep(10)


app_script_path = "/home/umair/Desktop/app.py"
loop_script_path = "/home/umair/Desktop/loop.py"
port = 5027

def is_running(script_name):
    try:
        output = subprocess.check_output(['pgrep', '-f', script_name])
        print(f"Running check output for {script_name}: {output.decode()}")
        return bool(output.strip())
    except subprocess.CalledProcessError:
        return False
def check_port_in_use(port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        in_use = sock.connect_ex(('localhost', port)) == 0
        print(f"Port {port} in use: {in_use}")
        return in_use

def start_script(script_path):
    print(f"Starting script: {script_path}")
    subprocess.Popen(['python3', script_path])

# Monitor app.py
if not is_running(app_script_path) and not check_port_in_use(port):
    print(f"{app_script_path} is not running and port {port} is available. Starting the script.")
    start_script(app_script_path)

time.sleep(10)

# Monitor loop.py
if not is_running(loop_script_path):
    print(f"{loop_script_path} is not running. Starting the script.")
    start_script(loop_script_path)
