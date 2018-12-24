#!/usr/bin/env python

import sys
import time

import cv2
import numpy as np
import yaml
from imutils.video import WebcamVideoStream

import vision.cv_utils as cv_utils
from vision import args


lower = np.array([0, 0, 0], dtype="uint8")
upper = np.array([0, 0, 0], dtype="uint8")

source = args['source']

# Use DirectShow if on Windows
if sys.platform == 'win32':
    source += cv2.CAP_DSHOW


def main():
    camera = WebcamVideoStream(src=source).start()

    cv2.namedWindow("Tuning")
    cv2.resizeWindow("Tuning", 700, 350)

    cv2.createTrackbar("Lower H", "Tuning", lower[0], 255,
                       lambda val: update_setting(True, 0, val))
    cv2.createTrackbar("Lower S", "Tuning", lower[1], 255,
                       lambda val: update_setting(True, 1, val))
    cv2.createTrackbar("Lower V", "Tuning", lower[2], 255,
                       lambda val: update_setting(True, 2, val))

    cv2.createTrackbar("Upper H", "Tuning", upper[0], 255,
                       lambda val: update_setting(False, 0, val))
    cv2.createTrackbar("Upper S", "Tuning", upper[1], 255,
                       lambda val: update_setting(False, 1, val))
    cv2.createTrackbar("Upper V", "Tuning", upper[2], 255,
                       lambda val: update_setting(False, 2, val))

    while True:
        im = camera.read()

        if im is not None:
            im = cv2.resize(im, (640, 480), 0, 0)

            blobs, mask = cv_utils.get_blob(cv2.cvtColor(im, cv2.COLOR_BGR2HSV), lower, upper)

            if blobs is not None:
                x1, y1, w1, h1 = cv2.boundingRect(blobs[0])

                # Draw image details
                im = cv_utils.draw_images(im, x1, y1, w1, h1)

            cv2.imshow("Original", im)

            if mask is not None:
                cv2.imshow("Mask", mask)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break


def update_setting(is_lower, index, value):
    if is_lower:
        lower[index] = value
    else:
        upper[index] = value


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        pass

    data = {
        "lower-color": lower.tolist(),
        "upper-color": upper.tolist()
    }

    with open("tuning_{}.yml".format(round(time.time())), "w") as outfile:
        yaml.dump(data, outfile)
