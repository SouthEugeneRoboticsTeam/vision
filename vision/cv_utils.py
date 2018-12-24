#!/usr/bin/env python

import cv2
import math
from . import args

verbose = args["verbose"]
horizontal_fov = args["horizontal_fov"]
vertical_fov = args["vertical_fov"]
target_width = args["target_width"]
target_height = args["target_height"]


def process_image(im, x1, y1, w1, h1):
    # Get image height and width
    height, width = im.shape[:2]

    # Find center of goal
    center_x = int(x1 + (x1 + w1)) / 2
    center_y = int(y1 + (y1 + h1)) / 2

    if verbose:
        print("[Goal] center: (%d, %d)" % (center_x, center_y))

    # Find pixels away from center
    offset_x_pixels = width / 2.0 - center_x * -1
    offset_y_pixels = height / 2.0 - center_y

    # Convert pixels from center to degrees
    offset_x_degrees = offset_x_pixels / horizontal_fov
    offset_y_degrees = offset_y_pixels / vertical_fov

    # Calculate distance from target using width and height, and take average
    width_value = math.tan(math.radians(width / (horizontal_fov * 2.0)))
    height_value = math.tan(math.radians(height / (vertical_fov * 2.0)))
    dist_width = (w1 / (target_width * 2.0 * width_value)) ** -1
    dist_height = (h1 / (target_height * 2.0 * height_value)) ** -1

    dist_avg = (dist_width + dist_height) / 2.0

    if verbose:
        print("[Goal] offset degrees: (%d, %d)" % (offset_x_degrees, offset_y_degrees))
        print("[Goal] distance: (w: %f, h: %f, avg: %f)" % (dist_width, dist_height, dist_avg))

    return offset_x_degrees, offset_y_degrees, dist_avg


def draw_images(im, x, y, w, h):
    # Parameters are image and blob dimensions

    # Get image height and width
    height, width = im.shape[:2]

    # Create before image
    im_rect = im.copy()

    # Draw rectangle around goal
    cv2.rectangle(im_rect, (x, y), (x + w, y + h), (255, 0, 0), 2)

    # Find center of goal
    center_x = int(0.5 * (x + (x + w)))
    center_y = int(0.5 * (y + (y + h)))

    if verbose:
        # Find pixels away from center
        offset_x = int(width / 2 - center_x) * -1
        offset_y = int(height / 2 - center_y)

        print("[Blob] center: (%d, %d)" % (center_x, center_y))
        print("[Blob] offset: (%d, %d)" % (offset_x, offset_y))

    # Draw point on center of goal
    cv2.circle(im_rect, (center_x, center_y), 2, (255, 0, 0), thickness=3)

    return im_rect


def get_blob(im, lower, upper):
    # Finds a blob, if one exists

    # Create mask of green
    try:
        green_mask = cv2.inRange(im, lower, upper)
    except cv2.error:
        # Catches the case where there is no blob in range
        return None, None

    # Get largest blob
    largest = get_largest(green_mask, 1)
    second_largest = get_largest(green_mask, 2)

    if largest is not None and second_largest is not None:
        return [largest, second_largest], green_mask
    else:
        return None, None


def get_largest(im, n):
    # Find contours of the shape
    major = cv2.__version__.split('.')[0]
    if major == '3':
        _, contours, _ = cv2.findContours(im.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    else:
        contours, _ = cv2.findContours(im.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # Create array of contour areas
    areas = [cv2.contourArea(contour) for contour in contours]

    # Sort array of areas by size
    sorted_areas = sorted(zip(areas, contours), key=lambda x: x[0], reverse=True)

    if sorted_areas and len(sorted_areas) >= n:
        # Find nth largest using data[n-1][1]
        return sorted_areas[n - 1][1]
    else:
        return None


def draw_offset(im, offset_x, offset_y, point, size, color):
    font = cv2.FONT_HERSHEY_SIMPLEX
    offset_string = "(" + str(offset_x) + ", " + str(offset_y) + ")"
    cv2.putText(im, offset_string, point, font, size, color)
