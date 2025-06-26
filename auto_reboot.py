import requests
import sys
import subprocess
from datetime import datetime

# Configuration
API_ENDPOINT = "https://REMOTE_HOST/api/healthcheck"  
SCHEDULED_REBOOT_TIME = "07:30:00"  # Format: HH:MM:SS
TIMEOUT_SECONDS = 300

def is_api_reachable(url):
    try:
        response = requests.get(url, timeout=TIMEOUT_SECONDS)
        return 200 <= response.status_code < 500
    except requests.RequestException:
        return False

def get_uptime_seconds():
    with open("/proc/uptime", "r") as f:
        return float(f.readline().split()[0])

def is_past_reboot_time(reboot_time_str):
    now = datetime.now().time()
    reboot_time = datetime.strptime(reboot_time_str, "%H:%M:%S").time()
    return now >= reboot_time

def main():
    if not is_api_reachable(API_ENDPOINT):
        print(f"API {API_ENDPOINT} not reachable. Exiting.")
        sys.exit(1)

    uptime_seconds = get_uptime_seconds()
    uptime_hours = uptime_seconds / 3600

    if uptime_hours > 24:
        print(f"Uptime is {uptime_hours:.2f} hours. Checking reboot schedule...")
        if is_past_reboot_time(SCHEDULED_REBOOT_TIME):
            print("Scheduled time passed. Rebooting system...")
            subprocess.run(["sudo", "reboot"])
        else:
            print("Scheduled reboot time not reached yet.")
    else:
        print(f"Uptime is {uptime_hours:.2f} hours. No reboot required.")

if __name__ == "__main__":
    main()
