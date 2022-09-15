#!/bin/sh
echo "Importing crontab..."
/usr/bin/crontab crontab.txt 
echo "Starting cron"
/usr/sbin/crond -f -L /dev/null