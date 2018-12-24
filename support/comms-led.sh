#!/usr/bin/env bash

HOST=10.25.21.2
GPIO=57

if [ ! -d /sys/class/gpio ]
then
    echo "Error: No GPIO system present, exiting"
    exit 1
fi

echo ${GPIO} > /sys/class/gpio/export
echo out > /sys/class/gpio/gpio${GPIO}/direction

num=0

while true
do
    if [ "$(timeout --preserve-status 0.15 ping -c 1 -W 1 ${HOST} &> /dev/null ; echo $?)" -ne "0" ]
    then
        ((num++))

        echo $((num % 2)) > /sys/class/gpio/gpio${GPIO}/value

        sleep 0.15
    else
        echo 1 > /sys/class/gpio/gpio${GPIO}/value

        sleep 5
    fi
done

echo 1 > /sys/class/gpio/gpio${GPIO}/value
echo ${GPIO} > /sys/class/gpio/unexport
