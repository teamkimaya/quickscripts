import json
import requests
import subprocess
import pytz
from datetime import datetime
import time
import os

CONFIG_FILE = 'config.json'  # Path to your JSON config

def load_config():
    with open(CONFIG_FILE, 'r') as f:
        config = json.load(f)
    return config['dateTimeUpdate']

def fetch_remote_time(api_url):
    try:
        response = requests.get(api_url, timeout=5)
        response.raise_for_status()
        data = response.json()
        # Assumes API returns something like {"timestamp": "2025-05-01T14:33:22Z"}
        return data['timestamp']
    except Exception as e:
        print(f"Error fetching time: {e}")
        return None

def set_system_time(utc_timestamp, timezone_str):
    try:
        # Convert to datetime object
        utc_time = datetime.strptime(utc_timestamp, "%Y-%m-%dT%H:%M:%SZ")
        utc_time = utc_time.replace(tzinfo=pytz.utc)

        # Convert to local time
        local_tz = pytz.timezone(timezone_str)
        local_time = utc_time.astimezone(local_tz)

        # Format time for `date` command
        time_str = local_time.strftime('%Y-%m-%d %H:%M:%S')
        print(f"Setting system time to: {time_str}")

        # Set system time
        subprocess.run(['sudo', 'date', '-s', time_str], check=True)

        # Set timezone
        subprocess.run(['sudo', 'timedatectl', 'set-timezone', timezone_str], check=True)
    except Exception as e:
        print(f"Error setting system time: {e}")

def main():
    config = load_config()
    timezone = config['timezone']
    api_url = config['api_url']
    interval = config.get('interval', 5)

    while True:
        timestamp = fetch_remote_time(api_url)
        if timestamp:
            set_system_time(timestamp, timezone)
        else:
            print("Failed to update time.")
        time.sleep(interval * 60)

if __name__ == "__main__":
    if os.geteuid() != 0:
        print("This script must be run as root.")
        exit(1)
    main()
