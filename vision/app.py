#!/usr/bin/env python

import os
import sys
import time

import cv2
import numpy as np
from imutils.video import WebcamVideoStream

import vision.cv_utils as cv_utils
from vision.network_utils import put, flush, table, settings_table
from vision.centroid_tracker import CentroidTracker
from . import args


class Vision:
    def __init__(self):
        self.args = args

        self.tracker = CentroidTracker()

        # Whether to start calculating distances/angles to the tracked target. Sent from the robot over NetworkTables
        self.locked = False
        self.lock_id = None

        # Dictionary of lower and upper HSV color values of blobs, min/max area of blobs, and min/max fullness of blobs
        self.settings = {
            'lower': np.array(self.args['lower_color']),
            'upper': np.array(self.args['upper_color']),

            'min_area': int(self.args['min_area']),
            'max_area': int(self.args['max_area']),

            'min_full': float(self.args['min_full']),
            'max_full': float(self.args['max_full']),
        }

        # Path to image
        self.image = self.args['image']

        # Whether to display results of processing in a new window
        self.display = self.args['display']

        # Whether to print log values to the console
        self.verbose = self.args['verbose']

        # Path to video source (or camera number if integer)
        self.source = self.args['source']
        if self.source.isdigit():
            self.source = int(self.source)

            if sys.platform == 'win32':
                self.source += cv2.CAP_DSHOW

        # Whether to display sliders to adjust settings
        self.tuning = self.args['tuning']

        # Put settings on NetworkTables
        self.put_settings()

        # Adds a listener that will set self.locked to the value in NT whenever the locked key is updated
        table.addEntryListener(self.lock_listener, immediateNotify=True, localNotify=True, key='locked')
        # Adds a listener that will update self.settings whenever a key on the settings table is updated
        settings_table.addEntryListener(self.settings_listener, immediateNotify=True, localNotify=True)

        if self.verbose:
            print(self.args)

    def run(self):
        if self.image is not None:
            self.run_image()
        else:
            self.run_video()

    def do_image(self, im):
        # Get all the contours in the image and the mask used to find them
        blobs, mask = cv_utils.get_blobs(im, self.settings['lower'], self.settings['upper'])

        # Don't process any blobs if vision isn't locked
        if not self.locked:
            self.tracker.deregister_all()
            return im, mask

        found_blob = False

        # Create list of rectangles that bound the blob
        bounding_rects = [cv2.boundingRect(blob) for blob in blobs]

        # Sort list of blobs by x-value and zip them together with their corresponding bounding rectangle
        sorted_blobs = sorted(zip(bounding_rects, blobs), key=lambda x: x[0], reverse=True)

        goals = []
        prev_target = None
        prev_blob = None
        for bounding_rect, blob in sorted_blobs:
            if blob is not None and mask is not None:
                # Get the location and size of the rectangle bounding the contour
                x, y, w, h = bounding_rect

                # Skip over the blob if its area is too small
                if w * h < self.settings['min_area']:
                    continue

                # Returns a rectangle of minimum area that bounds the blob (accounts for blobs at an angle)
                target = cv2.minAreaRect(blob)
                # Gets the coordinates of the 4 corners of the rectangle bounding the blob
                box = np.int0(cv2.boxPoints(target))

                # Straighten box to have a top-down view and get the transformed width and height
                transformed_box = cv_utils.four_point_transform(mask, box)
                width, height = transformed_box.shape

                # Calculate the proportion of the transformed box that's filled up by the blob
                full = cv_utils.get_percent_full(transformed_box)
                area = width * height

                # Check to make sure the box is sufficiently filled
                if self.settings['min_area'] <= area <= self.settings['max_area'] and self.settings['min_full'] <= full <= self.settings['max_full']:
                    if self.verbose:
                        print('[Goal] x: %d, y: %d, w: %d, h: %d, area: %d, full: %f, angle: %f' % (x, y, width, height, area, full, target[2]))

                    if self.display:
                        # Draw rectangles around goals and points on the center of the goal
                        im = cv_utils.draw_images(im, target, box)

                    if prev_target is not None:
                        sum = abs(prev_target[2]) - abs(target[2])
                        # Track both the left and right sides of the vision target
                        if sum < 0:
                            goals.append(((prev_target, target), (prev_blob, blob)))

                    # Left vision tape
                    prev_target = target
                    prev_blob = blob

        if len(goals) > 0:
            goal_centers = None

            try:
                # Calculate robot angle, target angle, x distance, y distance, distance, and centroid
                goal_centers = [cv_utils.process_image(im, goal[0], goal[1]) for goal in goals]
            except:
                pass

            if goal_centers is None:
                return im, mask

            # Zip goal centers with their corresponding goals and sort by the angle difference between robot and target
            possible_goals = sorted(zip(goal_centers, goals), key=lambda x: abs(x[0][0] + x[0][1]))

            objects = self.tracker.update([centers[5] for centers, _ in possible_goals])

            centers = None
            goal = None

            # Check if it's the first time locking onto the particular goal
            if self.lock_id is None:
                # Find the goal closest to where the robot is facing
                probable_goal = possible_goals[0]

                centers, goal = probable_goal
                # Assign an id to the goal based on the location of the centroid
                for index in objects:
                    if centers[5] == objects[index]:
                        self.lock_id = index
                        break
            else:
                try:
                    # Find the tracked goal that corresponds to the lock id
                    centers, goal = next(filter(lambda goal: goal[0][5] == objects[self.lock_id], possible_goals))
                except Exception:
                    print('Exception while finding goal with lock id')

            if centers is not None:
                robot_angle, target_angle, x_distance, y_distance, distance, _ = centers

                # Put calculations on NetworkTables
                put('distance', distance)
                put('x_distance', x_distance)
                put('y_distance', y_distance)
                put('robot_angle', robot_angle)
                put('target_angle', target_angle)

                found_blob = True

        put('found', found_blob)

        # Send the data to NetworkTables
        flush()

        return im, mask

    def run_image(self):
        if self.verbose:
            print('Image path specified, reading from %s' % self.image)

        bgr = cv2.imread(self.image)
        im = cv2.cvtColor(bgr, cv2.COLOR_BGR2HSV)
        im, mask = self.do_image(im)

        if self.display:
            # Show the images
            cv2.imshow('Original', cv2.cvtColor(im, cv2.COLOR_HSV2BGR))

            if mask is not None:
                cv2.imshow('Mask', mask)

            cv2.waitKey(0)
            cv2.destroyAllWindows()

    def run_video(self):
        if self.verbose:
            print('No image path specified, reading from camera video feed')

        # Start reading images from the camera
        camera = WebcamVideoStream(src=self.source).start()

        # Set stream size -- TODO: figure out why this isn't working
        # camera.stream.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        # camera.stream.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

        timeout = 0

        # Create trackbars to tune lower and upper HSV values if in tuning mode
        if self.tuning:
            cv2.namedWindow('Settings')
            cv2.resizeWindow('Settings', 700, 350)

            cv2.createTrackbar('Lower H', 'Settings', self.settings['lower'][0], 255,
                               lambda val: self.update_thresh(True, 0, val))
            cv2.createTrackbar('Lower S', 'Settings', self.settings['lower'][1], 255,
                               lambda val: self.update_thresh(True, 1, val))
            cv2.createTrackbar('Lower V', 'Settings', self.settings['lower'][2], 255,
                               lambda val: self.update_thresh(True, 2, val))

            cv2.createTrackbar('Upper H', 'Settings', self.settings['upper'][0], 255,
                               lambda val: self.update_thresh(False, 0, val))
            cv2.createTrackbar('Upper S', 'Settings', self.settings['upper'][1], 255,
                               lambda val: self.update_thresh(False, 1, val))
            cv2.createTrackbar('Upper V', 'Settings', self.settings['upper'][2], 255,
                               lambda val: self.update_thresh(False, 2, val))

        # Initializes array that stores raw camera frame outputs in the BGR color space
        bgr = np.zeros(shape=(360, 640, 3), dtype=np.uint8)
        # Initializes array that stores camera frame outputs in the HSV color space
        im = np.zeros(shape=(360, 640, 3), dtype=np.uint8)

        while True:
            # Fetches the most recent frame from the camera stream
            bgr = camera.read()

            if bgr is not None:
                # Resize raw camera frame and convert into HSV
                im = cv2.cvtColor(cv2.resize(bgr, (640, 360), 0, 0), cv2.COLOR_BGR2HSV)
                im, mask = self.do_image(im)

                # Display the original image and the masked image in two separate windows
                if self.display:
                    if im is not None:
                        cv2.imshow('Original', cv2.cvtColor(im, cv2.COLOR_HSV2BGR))
                    if mask is not None:
                        cv2.imshow('Mask', mask)

                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
            else:
                # Stop the program after 5 seconds if a camera hasn't been found
                if timeout == 0:
                    timeout = time.time()

                if time.time() - timeout > 5.0:
                    print('Camera search timed out!')
                    break

        if self.tuning:
            setting_names = ['Lower H', 'Lower S', 'Lower V', 'Upper H', 'Upper S', 'Upper V']

            # Create a settings directory if it doesn't exist
            if not os.path.exists('settings'):
                os.makedirs('settings')

            # Save new HSV values to a file in the settings directory
            with open('settings/save-{}.thr'.format(round(time.time() * 1000)), 'w') as thresh_file:
                values = enumerate(self.settings['lower'].tolist() + self.settings['upper'].tolist())
                thresh_file.writelines(['{}: {}\n'.format(setting_names[num], value[0])
                                        for num, value in values])

        camera.stop()
        cv2.destroyAllWindows()

    # Adjusts HSV thresholds
    def update_thresh(self, lower, index, value):
        if lower:
            self.settings['lower'][index] = value
        else:
            self.settings['upper'][index] = value

        self.put_settings()

    def lock_listener(self, source, key, value, is_new):
        self.locked = value

        if not value:
            self.lock_id = None

    # Updates settings with values sent over NetworkTables
    def settings_listener(self, source, key, value, is_new):
        key_parts = key.split('_')
        if key_parts[0] == 'lower' or key_parts[0] == 'upper':
            index = 0 if key_parts[1] == 'H' else 1 if key_parts[1] == 'S' in key else 2
            self.settings[key_parts[0]][index] = value
        else:
            self.settings[key] = value

    # Updates settings on NetworkTables
    def put_settings(self):
        for setting in self.settings:
            if setting == 'lower' or setting == 'upper':
                settings_table.putValue('{}_H'.format(setting), int(self.settings[setting][0][0]))
                settings_table.putValue('{}_S'.format(setting), int(self.settings[setting][1][0]))
                settings_table.putValue('{}_V'.format(setting), int(self.settings[setting][2][0]))
            else:
                settings_table.putValue(setting, self.settings[setting])
