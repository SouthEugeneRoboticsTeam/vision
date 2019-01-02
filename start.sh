#!/usr/bin/env bash

wait=15

echo "$(date) Sleeping $wait seconds..."
sleep ${wait}
echo "$(date) Running modprobe..."
modprobe uvcvideo nodrop=1 timeout=6000
lsusb
echo "$(date) Starting vision..."
python3 run.py
