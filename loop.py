import time
from datetime import datetime
from app import play_fajr_athan, play_regular_athan, get_prayer_times

def update_prayer_times():
    """Fetch and update prayer times from the API."""
    print("Updating prayer times...")
    try:
        prayer_times = get_prayer_times()
        print("Retrieved prayer times:", prayer_times)  # Debug print

        # Extract individual prayer times
        FAJR = prayer_times.get('fajr')
        DHUHR = prayer_times.get('dohr')
        ASR = prayer_times.get('asr')
        MAGHRIB = prayer_times.get('maghreb')
        ISHA = prayer_times.get('icha')

        print(f"Extracted times - FAJR: {FAJR}, DHUHR: {DHUHR}, ASR: {ASR}, MAGHRIB: {MAGHRIB}, ISHA: {ISHA}")
        return FAJR, DHUHR, ASR, MAGHRIB, ISHA

    except Exception as e:
        print(f"Error retrieving prayer times: {e}")
        return None, None, None, None, None

def main_loop():
    # Initialize prayer times
    FAJR, DHUHR, ASR, MAGHRIB, ISHA = update_prayer_times()

    # Infinite loop to update prayer times at 2 AM
    while True:
        current_time = datetime.now().strftime('%H:%M')

        # Check if it's 2 AM to update prayer times
        if current_time == "02:00":
            FAJR, DHUHR, ASR, MAGHRIB, ISHA = update_prayer_times()
            time.sleep(60)  # Sleep for a minute to avoid multiple updates within the same minute

        # Check for each prayer time and play the corresponding athan
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
