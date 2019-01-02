#!/usr/bin/env bash

export DISPLAY=:0

wait=5

echo "$(date) Sleeping $wait seconds..."
sleep ${wait}
echo "$(date) Starting GUI..."
python3 <DIRECTORY>/gui.py
