from flask import Flask, render_template, request, jsonify, redirect, url_for
from flask_socketio import SocketIO, emit
from datetime import datetime, timedelta
from mosques_data import mosques
from pygame import mixer
import subprocess
import threading
import schedule
import requests
import yt_dlp
import evdev
import json
import time
import os

app = Flask(__name__)
socketio = SocketIO(app) 
mixer.init()

# Initialize prayer_time_cache and last_fetched as global variables
prayer_time_cache = None
fajr_iqama = dhuhr_iqama = asr_iqama = maghrib_iqama = isha_iqama = None

# Mawaqit API Link for your local mosque
LinkAPI = "http://localhost:8000/api/v1/noor-dublin/prayer-times"

# Define directories for athan files
ATHANS_DIR = '/home/pi/Desktop/Athan-speaker-using-Raspberry-pi/Athans'
FAJR_ATHANS_DIR = '/home/pi/Desktop/Athan-speaker-using-Raspberry-pi/FajrAthans'
TEMP_DIR =  '/home/pi/Desktop/Athan-speaker-using-Raspberry-pi/Temp'
IQAMA_DIR = '/home/pi/Desktop/Athan-speaker-using-Raspberry-pi/Iqamas'


# File to store selected athans
SELECTION_FILE = '/home/pi/Desktop/Athan-speaker-using-Raspberry-pi/selected_athans.json'
VOLUME_FILE = '/home/pi/Desktop/Athan-speaker-using-Raspberry-pi/volume_setting.json'
IQAMA_FILE = '/home/pi/Desktop/Athan-speaker-using-Raspberry-pi/selected_iqama.json'
SETTINGS_FILE = '/home/pi/Desktop/Athan-speaker-using-Raspberry-pi/iqama_settings.json'
MOSQUE_FILE = '/home/pi/Desktop/Athan-speaker-using-Raspberry-pi/mosque_url.json'
device = evdev.InputDevice('/dev/input/event0')


# Function to load the mosque URL from the file
def load_mosque_url():
    if os.path.exists(MOSQUE_FILE):
        with open(MOSQUE_FILE, 'r') as f:
            return json.load(f).get('mosque_url')
    return ""

# Function to save mosque URL to a file
def save_mosque_url(mosque_url):
    with open(MOSQUE_FILE, 'w') as f:
        json.dump({'mosque_url': mosque_url}, f)  

# Function to load selected athans from file
def load_selected_athans():
    if os.path.exists(SELECTION_FILE):
        with open(SELECTION_FILE, 'r') as f:
            return json.load(f)
    else:
        return {
            'fajr': 'default_fajr.wav',
            'regular': 'default_regular.wav'
        }

# Function to save selected athans to file
def save_selected_athans(fajr_athan, regular_athan):
    with open(SELECTION_FILE, 'w') as f:
        json.dump({
            'fajr': fajr_athan,
            'regular': regular_athan
        }, f)

# Function to load selected iqama from file
def load_selected_iqama():    
    if os.path.exists(IQAMA_FILE):
        with open(IQAMA_FILE, 'r') as f: 
            return json.load(f)
    else:
        return 'Iqamat.mp3'
        
# Function to save selected iqama to file
def save_selected_iqama(iqama_file):    
    with open(IQAMA_FILE, 'w') as f:
        json.dump(iqama_file, f)

# Function to load iqama settings from a file
def load_iqama_settings():
    if os.path.exists(SETTINGS_FILE):
        try:
            with open(SETTINGS_FILE, 'r') as file:
                return json.load(file)
        except (json.JSONDecodeError, ValueError):
            print("Invalid settings file detected. Using default settings.")
    
    # Default settings if file is missing or invalid
    return {
        "fajr": {"enabled": False, "option": "delay", "delay": "", "manual_time": ""},
        "dhuhr": {"enabled": False, "option": "delay", "delay": "", "manual_time": ""},
        "asr": {"enabled": False, "option": "delay", "delay": "", "manual_time": ""},
        "maghrib": {"enabled": False, "option": "delay", "delay": "", "manual_time": ""},
        "isha": {"enabled": False, "option": "delay", "delay": "", "manual_time": ""}
    }

# Function to save iqama settings to a file
def save_iqama_settings(settings):
    with open(SETTINGS_FILE, 'w') as file:
        json.dump(settings, file, indent=4)

# Set alsamixer to 100%
subprocess.run(["amixer", "-M", "set", "PCM", "100%", "unmute"])

def set_volume(volume):
    mixer.music.set_volume(volume / 100)

# Function to load volume setting from file
def load_volume_setting():
    if os.path.exists(VOLUME_FILE):
        with open(VOLUME_FILE, 'r') as f:
            return json.load(f).get('volume', 50)  # Default to 50 if not found
    else:
        return 50  # Default to 50 if file does not exist

# Function to save volume setting to file
def save_volume_setting(volume):
    with open(VOLUME_FILE, 'w') as f:
        json.dump({'volume': volume}, f)


# Load initial selections and volume
selected_athan = load_selected_athans()
selected_iqama = load_selected_iqama() 
current_volume = load_volume_setting()
set_volume(current_volume)

def play_fajr_athan():
    try:
        file_path = os.path.join(FAJR_ATHANS_DIR, selected_athan['fajr'])
        mixer.music.load(file_path)
        set_volume(current_volume)
        mixer.music.play()
        while mixer.music.get_busy():
            time.sleep(1)
    except Exception as e:
        print(f"Error playing Fajr athan: {e}")

def play_regular_athan():
    try:
        file_path = os.path.join(ATHANS_DIR, selected_athan['regular'])
        mixer.music.load(file_path)
        set_volume(current_volume)
        mixer.music.play()
        while mixer.music.get_busy():
            time.sleep(1)
    except Exception as e:
        print(f"Error playing regular athan: {e}")

def play_iqama():
    try:
        file_path = os.path.join(IQAMA_DIR, selected_iqama)
        mixer.music.load(file_path)
        set_volume(current_volume)
        mixer.music.play()        
        while mixer.music.get_busy():
            time.sleep(1)
        time.sleep(60)
    except Exception as e:
        print(f"Error playing iqama: {e}")

def stop_athan():
    mixer.music.stop()

def get_prayer_times():
    global prayer_times_cache

    try:
        # Fetch prayer times from the API
        response = requests.get(LinkAPI)
        if response.status_code == 200:
            prayer_times = response.json()

            # Update the cache with the fetched prayer times
            prayer_times_cache = {
                'fajr_12hr': format_time(prayer_times.get('fajr', '')),
                'sunset_12hr': format_time(prayer_times.get('sunset', '')),
                'dohr_12hr': format_time(prayer_times.get('dohr', '')),
                'asr_12hr': format_time(prayer_times.get('asr', '')),
                'maghreb_12hr': format_time(prayer_times.get('maghreb', '')),
                'icha_12hr': format_time(prayer_times.get('icha', '')),
                'fajr': prayer_times.get('fajr', ''),
                'dohr': prayer_times.get('dohr', ''),
                'asr': prayer_times.get('asr', ''),
                'maghreb': prayer_times.get('maghreb', ''),
                'icha': prayer_times.get('icha', ''),
            }

        else:
            raise Exception(f"Failed to retrieve prayer times. Status code: {response.status_code}")

    except Exception as e:
        print(f"Error retrieving prayer times: {e}")
        return None  # Or return an empty dict if preferred

    # Return the fetched prayer times
    return prayer_times_cache


def format_time(time_str):
    """Convert 24-hour time format to 12-hour time format with AM/PM."""
    try:
        dt = datetime.strptime(time_str, '%H:%M')
        return dt.strftime('%I:%M %p')
    except ValueError:
        return time_str  # Return original if conversion fails

# Function to update iqama times whenever the iqama settings form is submitted
def update_iqama_times():
    global fajr_iqama, dhuhr_iqama, asr_iqama, maghrib_iqama, isha_iqama
    iqama_settings = load_iqama_settings()  # Load current iqama settings

    def calculate_iqama_time(prayer_key, athan_time_str):
        setting = iqama_settings.get(prayer_key, {})
        print(f"Calculating iqama time for {prayer_key}: setting={setting}, athan_time_str={athan_time_str}")
        
        if setting.get("enabled"):
            if setting["option"] == "manual" and setting["manual_time"]:
                print(f"Manual time for {prayer_key}: {setting['manual_time']}")
                return setting["manual_time"]
            elif setting["option"] == "delay" and setting["delay"]:
                delay_minutes = int(setting["delay"])
                athan_time = datetime.strptime(athan_time_str, "%H:%M")
                iqama_time = athan_time + timedelta(minutes=delay_minutes)
                iqama_str = iqama_time.strftime("%H:%M")
                print(f"Delay time for {prayer_key}: {iqama_str}")
                return iqama_str
        print(f"{prayer_key} is not enabled or settings are invalid")
        return None

    # Calculate each iqama time
    fajr_iqama = calculate_iqama_time("fajr", prayer_times_cache["fajr"])
    dhuhr_iqama = calculate_iqama_time("dhuhr", prayer_times_cache["dohr"])
    asr_iqama = calculate_iqama_time("asr", prayer_times_cache["asr"])
    maghrib_iqama = calculate_iqama_time("maghrib", prayer_times_cache["maghreb"])
    isha_iqama = calculate_iqama_time("isha", prayer_times_cache["icha"])

    print("Iqama times updated:", fajr_iqama, dhuhr_iqama, asr_iqama, maghrib_iqama, isha_iqama)


def handle_volume_buttons():
    global current_volume
    print("Listening for button presses...")  # Debugging log
    for event in device.read_loop():
        if event.type == evdev.ecodes.EV_KEY:
            key_event = evdev.categorize(event)
            print(f"Key event detected: {key_event}")  # Debugging log
            if key_event.keycode == 'KEY_VOLUMEUP' and key_event.keystate == evdev.KeyEvent.key_down:
                if current_volume < 100:
                    current_volume += 5
                    current_volume = min(100, current_volume)  # Ensure volume is between 0-100
                    set_volume(current_volume)
                    save_volume_setting(current_volume)
                    print(f"Volume increased to {current_volume}")  # Debugging log
                    socketio.emit('volume_update', {'volume': current_volume})

            elif key_event.keycode == 'KEY_VOLUMEDOWN' and key_event.keystate == evdev.KeyEvent.key_down:
                if current_volume > 0:
                    current_volume -= 5
                    current_volume = max(0, current_volume)  # Ensure volume is between 0-100
                    set_volume(current_volume)
                    save_volume_setting(current_volume)
                    print(f"Volume decreased to {current_volume}")  # Debugging log
                    socketio.emit('volume_update', {'volume': current_volume})
                  

def main_loop():
    # Load prayer times initially when the program starts
    prayer_times = get_prayer_times()

    # Check if prayer times were fetched successfully
    if not prayer_times:
        print("Failed to load prayer times. Exiting...")
        return  # Exit if prayer times cannot be fetched

    # Extract individual prayer times (24-hour format) once
    FAJR = prayer_times.get('fajr', '')
    DHUHR = prayer_times.get('dohr', '')
    ASR = prayer_times.get('asr', '')
    MAGHRIB = prayer_times.get('maghreb', '')
    ISHA = prayer_times.get('icha', '')

    while True:
        # Get the current time in 24-hour format (HH:MM)
        current_time = datetime.now().strftime('%H:%M')

        # Check if the current time matches any prayer time
        if current_time == FAJR:
            play_fajr_athan()
        elif current_time == DHUHR:
            play_regular_athan()
        elif current_time == ASR:
            play_regular_athan()
        elif current_time == MAGHRIB:
            play_regular_athan()
        elif current_time == ISHA:
            play_regular_athan()
        elif current_time == '09:50':
            play_regular_athan()

        # Sleep for a second before checking again
        time.sleep(1)  

def iqama_loop():
    
    while True:
        # Get the current time in HH:MM format
        current_time = datetime.now().strftime('%H:%M')
        
        # Check if each iqama time matches the current time
        if current_time == fajr_iqama:
            play_iqama()
        elif current_time == dhuhr_iqama:
            play_iqama()
        elif current_time == asr_iqama:
            play_iqama()
        elif current_time == maghrib_iqama:
            play_iqama()
        elif current_time == isha_iqama:
            play_iqama()

        # Sleep for 60 seconds to avoid repeated checks within the same minute
        time.sleep(1)

            
# Start the main loop in a separate thread
def start_background_thread():
    threading.Thread(target=main_loop, daemon=True).start()
    threading.Thread(target=iqama_loop, daemon=True).start()
    threading.Thread(target=handle_volume_buttons, daemon=True).start()


def download_athan_from_youtube(url, save_path):
    ydl_opts = {
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',

        }],
        'outtmpl': os.path.join(TEMP_DIR, '%(title)s.%(ext)s'),  # Save as title.mp3
        'no-wait': True,
        'noplaylist': True,  # Ensure only the single video is downloaded
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])

  
    # Find the .mp3 file in the TEMP_DIR and move it to the target folder
    for file in os.listdir(TEMP_DIR):
        if file.endswith('.mp3'):
            mp3_file = os.path.join(TEMP_DIR, file)
            os.rename(mp3_file, os.path.join(save_path, file))  # Move to save_path
            break

    # Cleanup: Delete any leftover .ytdl files if they exist
    for file in os.listdir(TEMP_DIR):
        if file.endswith('.webm.ytdl'):
            os.remove(os.path.join(save_path, file))


@app.route('/', methods=['GET', 'POST'])
def index():
    global selected_athan, current_volume, selected_iqama

    if request.method == 'POST':
        try:
            if 'save_changes' in request.form:
                # Save selected athans from the form
                selected_fajr_athan = request.form.get('fajr_audio')
                selected_regular_athan = request.form.get('regular_audio')
                selected_iqama = request.form.get('iqama_audio')
                
                # Update selected athans and save to file
                selected_athan = {
                    'fajr': selected_fajr_athan,
                    'regular': selected_regular_athan
                }
                save_selected_athans(selected_fajr_athan, selected_regular_athan)
                save_selected_iqama(selected_iqama)

            elif 'test_fajr' in request.form:
                # Play test Fajr athan
                play_fajr_athan()
            elif 'test_regular' in request.form:
                # Play test regular athan
                play_regular_athan()
            elif 'stop_athan' in request.form:
                # Stop currently playing athan
                stop_athan()
            elif 'reboot' in request.form:
                # Trigger Raspberry Pi reboot
                os.system('sudo reboot')

        except Exception as e:
            print(f"Error processing POST request: {e}")
            return "Internal Server Error", 500

    # Get the list of files from both directories
    try:
        fajr_athan_files = os.listdir(FAJR_ATHANS_DIR)
        regular_athan_files = os.listdir(ATHANS_DIR)
        iqama_files = os.listdir(IQAMA_DIR)
    except Exception as e:
        print(f"Error reading athan directories: {e}")
        fajr_athan_files = []
        regular_athan_files = []
        iqama_files = []

    # Get prayer times for display
    prayer_times = get_prayer_times()
    iqama_settings = load_iqama_settings()
    saved_mosque_url = load_mosque_url()


    return render_template('index.html',
                           fajr_athan_files=fajr_athan_files,
                           regular_athan_files=regular_athan_files,
                           iqama_files=iqama_files,
                           selected_fajr_athan=selected_athan['fajr'],
                           selected_regular_athan=selected_athan['regular'],
                           selected_iqama=selected_iqama,
                           iqama_settings=iqama_settings,
                           prayer_times=prayer_times,
                           volume=current_volume,
                           saved_mosque_url=saved_mosque_url)

@app.route('/upload_fajr_athan', methods=['POST'])
def upload_fajr_athan():
    if 'file' not in request.files:
        return redirect(url_for('index'))

    file = request.files['file']
    if file.filename == '':
        return redirect(url_for('index'))

    if file:
        filename = file.filename
        file.save(os.path.join(FAJR_ATHANS_DIR, filename))
        return redirect(url_for('index'))

@app.route('/upload_regular_athan', methods=['POST'])
def upload_regular_athan():
    if 'file' not in request.files:
        return redirect(url_for('index'))

    file = request.files['file']
    if file.filename == '':
        return redirect(url_for('index'))

    if file:
        filename = file.filename
        file.save(os.path.join(ATHANS_DIR, filename))
        return redirect(url_for('index'))

@app.route('/update_volume', methods=['POST'])
def update_volume():
    try:
        data = request.get_json()
        volume = int(data['volume'])
        if 1 <= volume <= 100:
            global current_volume
            current_volume = volume
            save_volume_setting(volume)
            set_volume(current_volume)
            return jsonify({'status': 'success', 'volume': volume})
        else:
            return jsonify({'status': 'error', 'message': 'Invalid volume level'})
    except Exception as e:
        print(f"Error updating volume: {e}")
        return jsonify({'status': 'error', 'message': 'Failed to update volume'})

@app.route('/test_fajr', methods=['POST'])
def test_fajr():
    try:
        play_fajr_athan()
        return jsonify({'status': 'success'})
    except Exception as e:
        print(f"Error testing Fajr athan: {e}")
        return jsonify({'status': 'error', 'message': 'Failed to play Fajr athan'})

@app.route('/test_regular', methods=['POST'])
def test_regular():
    try:
        play_regular_athan()
        return jsonify({'status': 'success'})
    except Exception as e:
        print(f"Error testing regular athan: {e}")
        return jsonify({'status': 'error', 'message': 'Failed to play regular athan'})

@app.route('/test_iqama', methods=['POST'])
def test_iqama():
    try:
        play_iqama()
        return jsonify({'status': 'success'})
    except Exception as e:
        print(f"Error testing iqama: {e}")
        return jsonify({'status': 'error', 'message': 'Failed to play iqama'})

@app.route('/stop_athan', methods=['POST'])
def stop_athan_route():
    try:
        stop_athan()  # Your function to stop the Athan
        return jsonify({'status': 'success'})
    except Exception as e:
        print(f"Error stopping Athan: {e}")
        return jsonify({'status': 'error', 'message': 'Failed to stop Athan'}), 500

# Route to handle Fajr Athan YouTube download
@app.route('/download_fajr_from_youtube', methods=['POST'])
def download_fajr_from_youtube():
    youtube_url = request.form.get('youtube_url')
    if youtube_url:
        download_athan_from_youtube(youtube_url, FAJR_ATHANS_DIR)
        return redirect(url_for('index'))  # Redirect to homepage or success page
    return "Error: No YouTube URL provided", 400

# Route to handle Regular Athan YouTube download
@app.route('/download_regular_from_youtube', methods=['POST'])
def download_regular_from_youtube():
    youtube_url = request.form.get('youtube_url')
    if youtube_url:
        download_athan_from_youtube(youtube_url, ATHANS_DIR)
        return redirect(url_for('index'))  # Redirect to homepage or success page
    return "Error: No YouTube URL provided", 400

# Route to handle Iqama YouTube download
@app.route('/download_iqama_from_youtube', methods=['POST'])
def download_iqama_from_youtube():
    youtube_url = request.form.get('youtube_url')
    if youtube_url:
        download_athan_from_youtube(youtube_url, IQAMA_DIR)
        return redirect(url_for('index'))  # Redirect to homepage or success page
    return "Error: No YouTube URL provided", 400

# Route to upload Iqama file directly
@app.route('/upload_iqama', methods=['POST'])
def upload_iqama():
    if 'file' not in request.files:
        return redirect(url_for('index'))

    file = request.files['file']
    if file.filename == '':
        return redirect(url_for('index'))

    if file:
        filename = file.filename
        file.save(os.path.join(IQAMA_DIR, filename))
        return redirect(url_for('index'))

# Route to handle saving iqama settings
@app.route('/save_iqama_settings', methods=['POST'])
def save_iqama_settings_route():
    iqama_settings = {}
    prayers = ['fajr', 'dhuhr', 'asr', 'maghrib', 'isha']
    
    for prayer in prayers:
        iqama_settings[prayer] = {
            'enabled': request.form.get(f'{prayer}_enabled') == 'on',
            'option': request.form.get(f'{prayer}_option'),
            'delay': request.form.get(f'{prayer}_delay'),
            'manual_time': request.form.get(f'{prayer}_manual_time')
        }
    
    save_iqama_settings(iqama_settings)
    update_iqama_times()
    return redirect(url_for('index'))

#Route to handle deleting Athan files
@app.route('/remove_athan', methods=['POST'])
def remove_athan():
    athan_to_remove = request.form.get('athan_to_remove')
    audio_type = request.form.get('audio_type')  # Get audio type (fajr or regular)

    if athan_to_remove:
        try:
            # Determine the directory based on the audio type
            if audio_type == 'fajr':
                file_path = os.path.join(FAJR_ATHANS_DIR, athan_to_remove)
            elif audio_type == 'regular':
                file_path = os.path.join(ATHANS_DIR, athan_to_remove)
            else:
                raise ValueError("Invalid audio type specified.")

            # Remove the file
            if os.path.exists(file_path):
                os.remove(file_path)
                print(f"{athan_to_remove} has been removed successfully.")
            else:
                print(f"{athan_to_remove} does not exist.")
        except Exception as e:
            print(f"Error removing {athan_to_remove}: {str(e)}")

    return jsonify({'status': 'success'})



@app.route('/update-mosque', methods=['POST'])
def update_mosque():
    global LinkAPI
    try:
        data = request.get_json()
        mosque_url = data.get('mosqueUrl')

        if mosque_url:
            # Extract the last part of the mosque URL
            mosque_identifier = mosque_url.split('/')[-1]

            # Update the LinkAPI with the new mosque identifier
            LinkAPI = f"http://localhost:8000/api/v1/{mosque_identifier}/prayer-times"

            # Save the mosque URL for persistence
            save_mosque_url(mosque_url)

            # Fetch the new prayer times
            get_prayer_times()

            return jsonify({'success': True})
        else:
            return jsonify({'success': False}), 400
    except Exception as e:
        print(f"Error updating mosque: {e}")
        return jsonify({'success': False}), 500


@app.route('/mosques')
def get_mosques():
    return jsonify(mosques)

# Start the background thread when the Flask app starts
start_background_thread()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
