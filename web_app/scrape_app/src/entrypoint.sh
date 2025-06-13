#!/bin/bash

# Dump runtime env vars to file for cron to use
printenv | grep -v "no_proxy" > /etc/environment

# Create the log file to be able to run tail
touch /var/log/cron.log

# Create cron job (runtime!)
#echo "* * * * * . /etc/environment; /usr/local/bin/python /app/src/scrape.py >> /var/log/cron.log 2>&1" > /etc/cron.d/scrape-cron
echo "$CRON_TIME . /etc/environment; /usr/local/bin/python /app/src/scrape.py >> /var/log/cron.log 2>&1" > /etc/cron.d/scrape-cron
chmod 0644 /etc/cron.d/scrape-cron
crontab /etc/cron.d/scrape-cron

# Start cron and keep container alive
cron &
tail -f /var/log/cron.log