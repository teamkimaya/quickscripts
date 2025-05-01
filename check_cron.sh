#!/bin/bash

CRON_JOB="0 7 * * * /home/pi/myscript.sh"

# Check if the cron job already exists
(crontab -l 2>/dev/null | grep -F "$CRON_JOB") > /dev/null

if [ $? -ne 0 ]; then
    # Add the cron job if not found
    (crontab -l 2>/dev/null; echo "$CRON_JOB") | crontab -
    echo "Cron job added."
else
    echo "Cron job already exists."
fi
