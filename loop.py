import time
from datetime import datetime
from app import get_prayer_times, play_fajr_athan, play_regular_athan

def main_loop():
    while True:
        # Load prayer times
        prayer_times = get_prayer_times()

        if not prayer_times:
            print("Failed to load prayer times. Retrying...")
            time.sleep(60)  # Wait 1 minute before retrying
            continue  # Retry the loop

        # Extract individual prayer times (24-hour format)
        FAJR = prayer_times.get('fajr', '')
        DHUHR = prayer_times.get('dohr', '')
        ASR = prayer_times.get('asr', '')
        MAGHRIB = prayer_times.get('maghreb', '')
        ISHA = prayer_times.get('icha', '')

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

        time.sleep(1)  # Sleep for a second before checking again

if __name__ == "__main__":
    main_loop()
