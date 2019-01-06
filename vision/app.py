#!/usr/bin/env python

import os
import sys
import time

import cv2
import numpy as np
from imutils.video import WebcamVideoStream

import vision.cv_utils as cv_utils
from vision.network_utils import put, flush
from . import args


class Vision:
    def __init__(self):
        self.args = args

        self.lower = np.array(self.args["lower_color"])
        self.upper = np.array(self.args["upper_color"])

        self.min_area = int(self.args["min_area"])
        self.max_area = int(self.args["max_area"])

        self.min_full = float(self.args["min_full"])
        self.max_full = float(self.args["max_full"])

        self.image = self.args["image"]

        self.display = self.args["display"]

        self.verbose = self.args["verbose"]

        self.source = self.args["source"]
        if sys.platform == 'win32':
            self.source += cv2.CAP_DSHOW

        self.tuning = self.args["tuning"]

        if self.verbose:
            print(self.args)

    def run(self):
        if self.image is not None:
            self.run_image()
        else:
            self.run_video()

    def do_image(self, im, blobs, mask):
        found_blob = False

        pairs = []

        # Create array of contour areas
        bounding_rects = [cv2.boundingRect(blob) for blob in blobs]

        # Sort array of blobs by x-value
        sorted_blobs = sorted(zip(bounding_rects, blobs), key=lambda x: x[0], reverse=True)

        goals = []
        prev_target = None
        for bounding_rect, blob in sorted_blobs:
            if blob is not None and mask is not None:
                x, y, w, h = bounding_rect

                if w * h < self.min_area:
                    continue

                target = cv2.minAreaRect(blob)
                box = np.int0(cv2.boxPoints(target))

                transformed_box = cv_utils.four_point_transform(mask, box)
                width, height = transformed_box.shape

                full = cv_utils.get_percent_full(transformed_box)
                area = width * height

                if self.min_area <= area <= self.max_area and self.min_full <= full <= self.max_full and (4.5 <= abs(target[2]) <= 24.5 or 65.5 <= abs(target[2]) <= 85.5):
                    if self.verbose:
                        print("[Goal] x: %d, y: %d, w: %d, h: %d, area: %d, full: %f, angle: %f" % (x, y, width, height, area, full, target[2]))

                    if self.display:
                        # Draw image details
                        im = cv_utils.draw_images(im, target, box)

                    if prev_target:
                        sum = abs(prev_target[2]) - abs(target[2])

                        if sum < 0: goals.append((prev_target, target))

                    prev_target = target

        goal_centers = [cv_utils.process_image(im, goal) for goal in goals]
        possible_goals = sorted(zip(goal_centers, goals), key=lambda x: abs(x[0][0]))

        if len(possible_goals) > 0:
            centers, goal = possible_goals[0]

            put("xOffset", centers[0])
            put("yOffset", centers[1])

            found_blob = True

        put("found", found_blob)

        # Send the data to NetworkTables
        flush()

        return im

    def run_image(self):
        if self.verbose:
            print("Image path specified, reading from %s" % self.image)

        bgr = cv2.imread(self.image)
        im = cv2.cvtColor(bgr, cv2.COLOR_BGR2HSV)

        blobs, mask = cv_utils.get_blobs(im, self.lower, self.upper)

        im = self.do_image(im, blobs, mask)

        if self.display:
            # Show the images
            cv2.imshow("Original", cv2.cvtColor(im, cv2.COLOR_HSV2BGR))

            if mask is not None:
                cv2.imshow("Mask", mask)

            cv2.waitKey(0)
            cv2.destroyAllWindows()

        self.kill_received = True

    def run_video(self):
        if self.verbose:
            print("No image path specified, reading from camera video feed")

        camera = WebcamVideoStream(src=self.source).start()

        timeout = 0

        if self.tuning:
            cv2.namedWindow("Settings")
            cv2.resizeWindow("Settings", 700, 350)

            cv2.createTrackbar("Lower H", "Settings", self.lower[0], 255,
                               lambda val: self.update_setting(True, 0, val))
            cv2.createTrackbar("Lower S", "Settings", self.lower[1], 255,
                               lambda val: self.update_setting(True, 1, val))
            cv2.createTrackbar("Lower V", "Settings", self.lower[2], 255,
                               lambda val: self.update_setting(True, 2, val))

            cv2.createTrackbar("Upper H", "Settings", self.upper[0], 255,
                               lambda val: self.update_setting(False, 0, val))
            cv2.createTrackbar("Upper S", "Settings", self.upper[1], 255,
                               lambda val: self.update_setting(False, 1, val))
            cv2.createTrackbar("Upper V", "Settings", self.upper[2], 255,
                               lambda val: self.update_setting(False, 2, val))

        while True:
            bgr = camera.read()

            if bgr is not None:
                im = cv2.cvtColor(bgr, cv2.COLOR_BGR2HSV)
                im = cv2.resize(im, (640, 480), 0, 0)

                blobs, mask = cv_utils.get_blobs(im, self.lower, self.upper)

                im = self.do_image(im, blobs, mask)

                if self.display:
                    cv2.imshow("Original", cv2.cvtColor(im, cv2.COLOR_HSV2BGR))
                    if mask is not None:
                        cv2.imshow("Mask", mask)

                if cv2.waitKey(1) & 0xFF == ord("q"):
                    self.kill_received = True
                    break
            else:
                if timeout == 0:
                    print("No camera detected... Retrying...")

                timeout += 1

                if timeout > 5000:
                    print("Camera search timed out!")
                    break

        if self.tuning:
            setting_names = ["Lower H", "Lower S", "Lower V", "Upper H", "Upper S", "Upper V"]

            if not os.path.exists("settings"):
                os.makedirs("settings")

            with open("settings/save-{}.thr".format(round(time.time() * 1000)), "w") as thresh_file:
                values = enumerate(self.lower.tolist() + self.upper.tolist())
                thresh_file.writelines(["{}: {}\n".format(setting_names[num], value[0])
                                        for num, value in values])

        camera.stop()
        cv2.destroyAllWindows()

    def update_setting(self, lower, index, value):
        if lower:
            self.lower[index] = value
        else:
            self.upper[index] = value
