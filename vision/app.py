#!/usr/bin/env python

import os
import sys
import time

import cv2
import numpy as np
from imutils.video import WebcamVideoStream

import vision.cv_utils as cv_utils
from vision.network_utils import put, flush, settings_table
from . import args


class Vision:
    def __init__(self):
        self.args = args

        self.settings = {
            'lower': np.array(self.args["lower_color"]),
            'upper': np.array(self.args["upper_color"]),

            'min_area': int(self.args["min_area"]),
            'max_area': int(self.args["max_area"]),

            'min_full': float(self.args["min_full"]),
            'max_full': float(self.args["max_full"]),
        }

        self.image = self.args["image"]

        self.display = self.args["display"]

        self.verbose = self.args["verbose"]

        self.source = self.args["source"]
        if self.source.isdigit():
            self.source = int(self.source)

            if sys.platform == "win32":
                self.source += cv2.CAP_DSHOW

        self.tuning = self.args["tuning"]

        self.put_settings()

        settings_table.addEntryListener(self.settings_listener, immediateNotify=True, localNotify=True)

        if self.verbose:
            print(self.args)

    def run(self):
        if self.image is not None:
            self.run_image()
        else:
            self.run_video()

    def do_image(self, im, blobs, mask):
        found_blob = False

        # Create array of contour areas
        bounding_rects = [cv2.boundingRect(blob) for blob in blobs]

        # Sort array of blobs by x-value
        sorted_blobs = sorted(zip(bounding_rects, blobs), key=lambda x: x[0], reverse=True)

        goals = []
        prev_target = None
        for bounding_rect, blob in sorted_blobs:
            if blob is not None and mask is not None:
                x, y, w, h = bounding_rect

                if w * h < self.settings['min_area']:
                    continue

                target = cv2.minAreaRect(blob)
                box = np.int0(cv2.boxPoints(target))

                transformed_box = cv_utils.four_point_transform(mask, box)
                width, height = transformed_box.shape

                full = cv_utils.get_percent_full(transformed_box)
                area = width * height

                if self.settings['min_area'] <= area <= self.settings['max_area'] and self.settings['min_full'] <= full <= self.settings['max_full']:
                    if self.verbose:
                        print("[Goal] x: %d, y: %d, w: %d, h: %d, area: %d, full: %f, angle: %f" % (x, y, width, height, area, full, target[2]))

                    if self.display:
                        # Draw image details
                        im = cv_utils.draw_images(im, target, box)

                    if prev_target:
                        sum = abs(prev_target[2]) - abs(target[2])

                        if sum < 0:
                            goals.append((prev_target, target))

                    prev_target = target

        goal_centers = [cv_utils.process_image(im, goal) for goal in goals]
        possible_goals = sorted(zip(goal_centers, goals), key=lambda x: abs(x[0][0]))

        if len(possible_goals) > 0:
            centers, goal = possible_goals[0]

            robot_angle, target_angle, x_distance, y_distance, distance = centers

            put("distance", distance)
            put("x_distance", x_distance)
            put("y_distance", y_distance + 16.0) # Add 1/2 robot length
            put("robot_angle", robot_angle)
            put("target_angle", target_angle)

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

        blobs, mask = cv_utils.get_blobs(im, self.settings['lower'], self.settings['upper'])

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

        # Set stream size -- TODO: figure out why this isn't working
        # camera.stream.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        # camera.stream.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

        timeout = 0

        if self.tuning:
            cv2.namedWindow("Settings")
            cv2.resizeWindow("Settings", 700, 350)

            cv2.createTrackbar("Lower H", "Settings", self.settings['lower'][0], 255,
                               lambda val: self.update_thresh(True, 0, val))
            cv2.createTrackbar("Lower S", "Settings", self.settings['lower'][1], 255,
                               lambda val: self.update_thresh(True, 1, val))
            cv2.createTrackbar("Lower V", "Settings", self.settings['lower'][2], 255,
                               lambda val: self.update_thresh(True, 2, val))

            cv2.createTrackbar("Upper H", "Settings", self.settings['upper'][0], 255,
                               lambda val: self.update_thresh(False, 0, val))
            cv2.createTrackbar("Upper S", "Settings", self.settings['upper'][1], 255,
                               lambda val: self.update_thresh(False, 1, val))
            cv2.createTrackbar("Upper V", "Settings", self.settings['upper'][2], 255,
                               lambda val: self.update_thresh(False, 2, val))

        bgr = np.zeros(shape=(480, 640, 3), dtype=np.uint8)
        im = np.zeros(shape=(480, 640, 3), dtype=np.uint8)

        while True:
            bgr = camera.read()

            if bgr is not None:
                im = cv2.cvtColor(cv2.resize(bgr, (640, 480), 0, 0), cv2.COLOR_BGR2HSV)

                blobs, mask = cv_utils.get_blobs(im, self.settings['lower'], self.settings['upper'])

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
                    timeout = time.time()

                if time.time() - timeout > 5.0:
                    print("Camera search timed out!")
                    break

        if self.tuning:
            setting_names = ["Lower H", "Lower S", "Lower V", "Upper H", "Upper S", "Upper V"]

            if not os.path.exists("settings"):
                os.makedirs("settings")

            with open("settings/save-{}.thr".format(round(time.time() * 1000)), "w") as thresh_file:
                values = enumerate(self.settings['lower'].tolist() + self.settings['upper'].tolist())
                thresh_file.writelines(["{}: {}\n".format(setting_names[num], value[0])
                                        for num, value in values])

        camera.stop()
        cv2.destroyAllWindows()

    def update_thresh(self, lower, index, value):
        if lower:
            self.settings['lower'][index] = value
        else:
            self.settings['upper'][index] = value

        self.put_settings()

    def settings_listener(self, source, key, value, isNew):
        key_parts = key.split('_')
        if key_parts[0] == 'lower' or key_parts[0] == 'upper':
            index = 0 if key_parts[1] == 'H' else 1 if key_parts[1] == 'S' in key else 2
            self.settings[key_parts[0]][index] = value
        else:
            self.settings[key] = value

    def put_settings(self):
        for setting in self.settings:
            if setting == 'lower' or setting == 'upper':
                settings_table.putValue('{}_H'.format(setting), int(self.settings[setting][0][0]))
                settings_table.putValue('{}_S'.format(setting), int(self.settings[setting][1][0]))
                settings_table.putValue('{}_V'.format(setting), int(self.settings[setting][2][0]))
            else:
                settings_table.putValue(setting, self.settings[setting])
