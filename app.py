from flask import Flask, render_template, request, jsonify
import os
import json
import requests
from datetime import datetime
from pygame import mixer
import schedule
import time
import threading

app = Flask(__name__)

# Define directories for athan files
ATHANS_DIR = '/home/umair/Desktop/Athans'
FAJR_ATHANS_DIR = '/home/umair/Desktop/FajrAthans'

# File to store selected athans
SELECTION_FILE = '/home/umair/selected_athans.json'
VOLUME_FILE = '/home/umair/volume_setting.json'

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
current_volume = load_volume_setting()

def play_fajr_athan():
    try:
        file_path = os.path.join(FAJR_ATHANS_DIR, selected_athan['fajr'])
        mixer.init()
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
        mixer.init()
        mixer.music.load(file_path)
        set_volume(current_volume)
        mixer.music.play()
        while mixer.music.get_busy():
            time.sleep(1)
    except Exception as e:
        print(f"Error playing regular athan: {e}")

def stop_athan():
    mixer.music.stop()

def set_volume(volume):
    mixer.music.set_volume(volume / 100)

def get_prayer_times():
    try:
        response = requests.get("http://localhost:8000/api/v1/noor-dublin/prayer-times")
        if response.status_code == 200:
            prayer_times = response.json()

            return {
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


def format_time(time_str):
    """Convert 24-hour time format to 12-hour time format with AM/PM."""
    try:
        dt = datetime.strptime(time_str, '%H:%M')
        return dt.strftime('%I:%M %p')
    except ValueError:
        return time_str  # Return original if conversion fails


@app.route('/', methods=['GET', 'POST'])
def index():
    global selected_athan, current_volume

    if request.method == 'POST':
        try:
            if 'save_changes' in request.form:
                # Save selected athans from the form
                selected_fajr_athan = request.form.get('fajr_audio')
                selected_regular_athan = request.form.get('regular_audio')

                # Update selected athans and save to file
                selected_athan = {
                    'fajr': selected_fajr_athan,
                    'regular': selected_regular_athan
                }
                save_selected_athans(selected_fajr_athan, selected_regular_athan)

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
    except Exception as e:
        print(f"Error reading athan directories: {e}")
        fajr_athan_files = []
        regular_athan_files = []

    # Get prayer times for display
    prayer_times = get_prayer_times()

    return render_template('index.html',
                           fajr_athan_files=fajr_athan_files,
                           regular_athan_files=regular_athan_files,
                           selected_fajr_athan=selected_athan['fajr'],
                           selected_regular_athan=selected_athan['regular'],
                           prayer_times=prayer_times,
                           volume=current_volume)

@app.route('/update_volume', methods=['POST'])
def update_volume():
    try:
        data = request.get_json()
        volume = int(data['volume'])
        if 1 <= volume <= 100:
            global current_volume
            current_volume = volume
            save_volume_setting(volume)
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

@app.route('/stop_athan', methods=['POST'])
def stop_athan_route():
    try:
        stop_athan()
        return jsonify({'status': 'success'})
    except Exception as e:
        print(f"Error stopping athan: {e}")
        return jsonify({'status': 'error', 'message': 'Failed to stop athan'})


def update_prayer_times_daily():
    while True:
        current_time = datetime.now().strftime('%H:%M')

        # Check if it's 2:00 AM
        if current_time == "02:00":
            prayer_times = get_prayer_times()  # Call the function to get prayer times
            print(f"Prayer times updated at {current_time}")

            # Sleep until 2:01 AM to ensure the update doesn't happen multiple times within the same minute
            time.sleep(60)

        time.sleep(600)  # Sleep for 10 minutes before checking again


if __name__ == '__main__':

    # Start the daily update in a separate thread
    threading.Thread(target=update_prayer_times_daily, daemon=True).start()

    # Start Flask server
    app.run(host='0.0.0.0', port=5027, debug=True)
