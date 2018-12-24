#!/usr/bin/env bash

# This script is for installing the support files on a coprocessor, including the
# udev and v4l2 settings scripts which set the webcam's properties when it is
# plugged in, and the vision service which enables the script to start when the
# device is booted.

V4L2_INSTALL=/usr/local/bin/config-v4l2.sh
UDEV_INSTALL=/etc/udev/rules.d/99-webcam.rules
VISION_SERVICE_INSTALL=/etc/init.d/vision
COMMS_SERVICE_INSTALL=/etc/init.d/comms

if [ ! -d "support" ]; then
  echo "Error: Please run from the root directory of this repository"
  exit 1
fi

if [ "$EUID" -ne 0 ]; then
  echo "Error: Please run as root"
  exit 1
fi

# Install V4L2 config script
echo "Installing V4L2 config script in $V4L2_INSTALL..."
cp support/config-v4l2.sh ${V4L2_INSTALL}
chmod a+x ${V4L2_INSTALL}

# Install udev script
echo "Installing udev script in $UDEV_INSTALL..."
cp support/99-webcam.rules ${UDEV_INSTALL}
chmod a+x ${UDEV_INSTALL}

# Install vision service
echo "Installing vision service in $VISION_SERVICE_INSTALL..."
cp support/vision ${VISION_SERVICE_INSTALL}
chmod a+x ${VISION_SERVICE_INSTALL}
sed -i -e "s|<DIRECTORY>|$(pwd)|g" ${VISION_SERVICE_INSTALL}
sed -i -e "s|<USER>|$(whoami)|g" ${VISION_SERVICE_INSTALL}
update-rc.d vision defaults

# Install comms service
echo "Installing comms service in $COMMS_SERVICE_INSTALL..."
cp support/comms ${COMMS_SERVICE_INSTALL}
chmod a+x ${COMMS_SERVICE_INSTALL}
sed -i -e "s|<DIRECTORY>|$(pwd)|g" ${COMMS_SERVICE_INSTALL}
sed -i -e "s|<USER>|$(whoami)|g" ${COMMS_SERVICE_INSTALL}
update-rc.d comms defaults

echo "Script installation complete!"

echo -e "GET http://google.com HTTP/1.0\n\n" | nc google.com 80 > /dev/null 2>&1

if [ $? -eq 0 ]; then
    echo "Installing dependencies..."
    apt-get install -y -qq v4l-utils
    echo "Completing installation..."
else
    echo "No internet connection. Completing installation..."
fi

echo "Done!"
