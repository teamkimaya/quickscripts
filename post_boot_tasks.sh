#!/bin/bash

# Log start
echo "[INFO] Starting post boot tasks at $(date)" >> /home/pi/post_boot.log

# Find all boot scripts in /home/pi/scripts/ that match the pattern boot_*_*.sh
# and sort them numerically to ensure proper execution order
echo "[INFO] Finding boot scripts..." >> /home/pi/post_boot.log

# Find all boot scripts and sort them
boot_scripts=$(find /home/pi/scripts/ -type f -name "boot_*_*.sh" | sort)

# Log found scripts
echo "[INFO] Found the following boot scripts:" >> /home/pi/post_boot.log
echo "$boot_scripts" >> /home/pi/post_boot.log

# Execute each script in sequence
for script in $boot_scripts; do
    echo "[INFO] Executing $script at $(date)" >> /home/pi/post_boot.log
    $script >> /home/pi/post_boot.log 2>&1
    exit_code=$?
    echo "[INFO] Script $script completed with exit code: $exit_code" >> /home/pi/post_boot.log
done

# Log end
echo "[INFO] Finished post boot tasks at $(date)" >> /home/pi/post_boot.log
