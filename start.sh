#!/usr/bin/env bash

wait=15

# Camera paths (note: these paths are static by USB port -- if USB port changes, this path must change)
hatch_cam="/dev/v4l/by-path/platform-70090000.xusb-usb-0:3.1:1.0-video-index0"
cargo_cam="/dev/v4l/by-path/platform-70090000.xusb-usb-0:3.3:1.0-video-index0"

echo "$(date) Sleeping $wait seconds..."
sleep ${wait}
echo "$(date) Running modprobe..."
modprobe uvcvideo nodrop=1 timeout=6000
lsusb
echo "$(date) Starting vision..."

python3 run.py -s ${hatch_cam} -n hatch &
python3 run.py -s ${cargo_cam} -n cargo &
