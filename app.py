from flask import Flask, render_template, request, jsonify, redirect, url_for
import os
import json
import requests
from datetime import datetime
from pygame import mixer
import schedule
import time
import threading
import yt_dlp
from evdev import InputDevice, ecodes, categorize

app = Flask(__name__)

# Initialize prayer_time_cache and last_fetched as global variables
prayer_time_cache = None
last_fetched = None

# Mawaqit API Link for your local mosque
LinkAPI = "http://localhost:8000/api/v1/noor-dublin/prayer-times"

# Define directories for athan files
ATHANS_DIR = '/home/pi/Desktop/Athan-speaker-using-Raspberry-pi/Athans'
FAJR_ATHANS_DIR = '/home/pi/Desktop/Athan-speaker-using-Raspberry-pi/FajrAthans'

# File to store selected athans
SELECTION_FILE = '/home/pi/Desktop/Athan-speaker-using-Raspberry-pi/selected_athans.json'
VOLUME_FILE = '/home/pi/Desktop/Athan-speaker-using-Raspberry-pi/volume_setting.json'

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

def set_volume(volume):
    mixer.init()
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

def stop_athan():
    mixer.music.stop()

def get_prayer_times():
    global prayer_times_cache, last_fetched

    # Get the current time
    now = datetime.now()

    # If last_fetched is None (first run) or it’s a new day, or if it’s exactly 2 AM, fetch new prayer times
    if last_fetched is None or (now.date() != last_fetched.date()) or (now.hour == 2 and now.minute == 0):
        try:
            response = requests.get(LinkAPI)
            if response.status_code == 200:
                prayer_times = response.json()

                # Update the cache and last fetched time
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
                last_fetched = now
            else:
                raise Exception(f"Failed to retrieve prayer times. Status code: {response.status_code}")
        except Exception as e:
            print(f"Error retrieving prayer times: {e}")
            return None  # Or return an empty dict if preferred

    # Return the cached prayer times
    return prayer_times_cache


def format_time(time_str):
    """Convert 24-hour time format to 12-hour time format with AM/PM."""
    try:
        dt = datetime.strptime(time_str, '%H:%M')
        return dt.strftime('%I:%M %p')
    except ValueError:
        return time_str  # Return original if conversion fails

def main_loop():
    # Load prayer times initially when the program starts
    prayer_times = get_prayer_times()

    last_updated_date = None  # To track the last date the prayer times were updated

    while True:
        current_time = datetime.now().strftime('%H:%M')
        current_date = datetime.now().date()

        # Update prayer times at 2:00 AM
        if current_time == "02:00" and last_updated_date != current_date:
            prayer_times = get_prayer_times()

            if not prayer_times:
                print("Failed to load prayer times. Retrying in 1 minute...")
                time.sleep(60)  # Wait 1 minute before retrying
                continue  # Retry the loop

            last_updated_date = current_date  # Set the last updated date
            print("Prayer times updated at 2:00 AM.")

        # Extract individual prayer times (24-hour format)
        FAJR = prayer_times.get('fajr', '')
        DHUHR = prayer_times.get('dohr', '')
        ASR = prayer_times.get('asr', '')
        MAGHRIB = prayer_times.get('maghreb', '')
        ISHA = prayer_times.get('icha', '')

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

        time.sleep(1)  # Sleep for a second before checking again

# Background thread to listen for USB speaker volume button presses
def listen_for_volume_buttons():
    device = InputDevice('/dev/input/event0')  # Replace with the correct event file for your device
    global current_volume
    
    for event in device.read_loop():
        if event.type == ecodes.EV_KEY:
            key_event = categorize(event)
            
            # Check for volume down key
            if key_event.keycode == 'KEY_VOLUMEDOWN' and key_event.keystate == key_event.key_down:
                if current_volume > 0:
                    current_volume -= 5
                    set_volume(current_volume)
                    save_volume_setting(current_volume)
                print(f"Volume Down: {current_volume}")
            
            # Check for volume up key
            elif key_event.keycode == 'KEY_VOLUMEUP' and key_event.keystate == key_event.key_down:
                if current_volume < 100:
                    current_volume += 5
                    set_volume(current_volume)
                    save_volume_setting(current_volume)
                print(f"Volume Up: {current_volume}")
                
# Start the main loop in a separate thread
def start_background_thread():
    threading.Thread(target=main_loop, daemon=True).start()
    threading.Thread(target=listen_for_volume_buttons, daemon=True).start()

def download_athan_from_youtube(url, save_path):
    ydl_opts = {
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',

        }],
        'outtmpl': os.path.join(save_path, '%(title)s.%(ext)s'),  # Save as title.mp3
        'no-wait': True,
        'noplaylist': True,  # Ensure only the single video is downloaded
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])

    # Cleanup: Delete any leftover .ytdl files if they exist
    for file in os.listdir(save_path):
        if file.endswith('.webm.ytdl'):
            os.remove(os.path.join(save_path, file))



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

@app.route('/get_volume', methods=['GET'])
def get_volume():
    try:
        return jsonify({'status': 'success', 'volume': current_volume})
    except Exception as e:
        print(f"Error getting volume: {e}")
        return jsonify({'status': 'error', 'message': 'Failed to get volume'})


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

    return redirect(url_for('index'))  # Redirect back to the index view

# Start the background thread when the Flask app starts
start_background_thread()

if __name__ == '__main__':
    # Start Flask server
    app.run(host='0.0.0.0', port=5000, debug=True)
