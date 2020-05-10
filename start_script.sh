#!/usr/bin/env bash
#Configure web server

cd /usr/src/app 

#TODO: start cron jobs
# change python environment
source activate emission-calendar

# launch the webapp
./e-mission-py.bash pm.py
