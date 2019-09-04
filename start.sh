#!/usr/bin/env bash

wait=15

# Camera paths (note: these paths are static by USB port -- if USB port changes, this path must change)
cargo_cam="/dev/v4l/by-path/platform-70090000.xusb-usb-0:3.3:1.0-video-index0"

start_camera() {
  while true; do
    python3 run.py -n $1 -s $2
  done
}

echo "$(date) Sleeping $wait seconds..."
sleep ${wait}
echo "$(date) Running modprobe..."
modprobe uvcvideo nodrop=1 timeout=6000
lsusb
echo "$(date) Starting vision..."

start_camera cargo ${cargo_cam} &
