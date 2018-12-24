#!/usr/bin/env bash

log=/var/log/config-v4l2.log

if [ -z "$1" ]
then
  echo "Usage: $0 <device>"
  exit 1
fi

v4l2-ctl --device $1 \
  -c brightness=30 \
  -c contrast=8 \
  -c saturation=100 \
  -c white_balance_temperature_auto=0 \
  -c power_line_frequency=0 \
  -c white_balance_temperature=5000 \
  -c sharpness=25 \
  -c backlight_compensation=0 \
  -c exposure_auto=1 \
  -c exposure_absolute=5 \
  &>> "$log"

if [ "$?" == "0" ]
then
  echo "Done configuring $1" | tee -a "$log"
  exit 0
else
  echo "Error configuring $1" | tee -a "$log"
  exit 1
fi
