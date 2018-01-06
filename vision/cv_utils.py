#!/usr/bin/env python

import cv2
from . import args

verbose = args["verbose"]


def process_image(im, x1, y1, w1, h1, x2, y2, w2, h2):
    # Get image height and width
    height, width = im.shape[:2]

    if verbose:
        print("[Image] width: %d, height: %d" % (width, height))

    offset_x = 0
    offset_y = 0

    # Find center of goal
    center_x = (int(0.5 * (x1 + (x1 + w1))) + int(0.5 * (x2 + (x2 + w2)))) / 2
    center_y = (int(0.5 * (y1 + (y1 + h1))) + int(0.5 * (y2 + (y2 + h2)))) / 2

    if verbose:
        print("[Goal] center: (%d, %d)" % (center_x, center_y))

    # Find pixels away from center
    offset_x = int(width / 2 - center_x) * -1
    offset_y = int(height / 2 - center_y)

    if verbose:
        print("[Goal] offset: (%d, %d)" % (offset_x, offset_y))

    return offset_x, offset_y


def draw_images(im, x, y, w, h, side):
    # Parameters are image and blob dimensions

    # Get image height and width
    height, width = im.shape[:2]

    if verbose:
        print("[Image] width: %d, height: %d" % (width, height))

    # Create before image
    im_rect = im.copy()

    # Draw rectangle around goal
    cv2.rectangle(im_rect, (x, y), (x + w, y + h), (255, 0, 0), 2)

    # Find center of goal
    center_x = int(0.5 * (x + (x + w)))
    center_y = int(0.5 * (y + (y + h)))

    if verbose:
        print("[Blob] center: (%d, %d)" % (center_x, center_y))

    # Find pixels away from center
    offset_x = int(width / 2 - center_x) * -1
    offset_y = int(height / 2 - center_y)

    if verbose:
        print("[Blob] offset: (%d, %d)" % (offset_x, offset_y))

    # Draw point on center of goal
    cv2.circle(im_rect, (center_x, center_y), 2, (255, 0, 0), thickness=3)

    # Put text on screen
    if side is True:
        draw_offset(im_rect, offset_x, offset_y, (0, 30), 1, (255, 255, 255))
    else:
        draw_offset(im_rect, offset_x, offset_y, (400, 30), 1, (255, 255, 255))

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

    # Cycle through contours and add area to array
    areas = []
    for c in contours:
        areas.append(cv2.contourArea(c))

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
