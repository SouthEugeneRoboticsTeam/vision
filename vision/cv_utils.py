#!/usr/bin/env python

import math

import cv2
import numpy as np
import imutils

from . import args

verbose = args["verbose"]
horizontal_fov = args["horizontal_fov"]
vertical_fov = args["vertical_fov"]
target_width = args["target_width"]
target_height = args["target_height"]
calculate_distances = args["calculate_distances"]


def process_image(im, rect):
    # Get image height and width
    height, width = im.shape[:2]

    # Find center of goal
    center_x = rect[0][0]
    center_y = rect[0][1]

    # Find pixels away from center
    offset_x_pixels = (width / 2.0 - center_x) * -1
    offset_y_pixels = height / 2.0 - center_y

    offset_x_percent = offset_x_pixels / (width / 2.0)
    offset_y_percent = offset_y_pixels / (height / 2.0)

    # Convert pixels from center to degrees
    offset_x_degrees = offset_x_percent * horizontal_fov / 2.0
    offset_y_degrees = offset_y_percent * vertical_fov / 2.0

    if verbose:
        print("[Goal] center: (%d, %d)" % (center_x, center_y))
        print("[Goal] offset pixels: (%d, %d)" % (offset_x_pixels, offset_y_pixels))
        print("[Goal] offset degrees: (%f, %f)" % (offset_x_degrees, offset_y_degrees))

    return offset_x_degrees, offset_y_degrees


def draw_images(im, rect, box):
    # Create before image
    im_rect = im.copy()

    # Draw rectangle around goal
    cv2.drawContours(im_rect, [box], 0, (255, 0, 0), 2)

    # Find center of goal
    center_x = int(rect[0][0])
    center_y = int(rect[0][1])

    # Draw point on center of goal
    cv2.circle(im_rect, (center_x, center_y), 2, (255, 0, 0), thickness=3)

    return im_rect


def get_blob(im, lower, upper):
    # Finds a blob, if one exists

    # Create mask of green
    try:
        mask = cv2.inRange(im, lower, upper)
    except cv2.error:
        # Catches the case where there is no blob in range
        return None, None

    # Get largest blob
    largest = get_largest(mask, 1)

    if largest is not None:
        return largest, mask
    else:
        return None, None


def get_largest(im, n):
    # Find contours of the shape
    contours = cv2.findContours(im.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    contours = imutils.grab_contours(contours)

    # Create array of contour areas
    areas = [cv2.contourArea(contour) for contour in contours]

    # Sort array of areas by size
    sorted_areas = sorted(zip(areas, contours), key=lambda x: x[0], reverse=True)

    if sorted_areas and len(sorted_areas) >= n:
        # Find nth largest
        return sorted_areas[n - 1][1]
    else:
        return None


def draw_offset(im, offset_x, offset_y, point, size, color):
    font = cv2.FONT_HERSHEY_SIMPLEX
    offset_string = "(" + str(offset_x) + ", " + str(offset_y) + ")"
    cv2.putText(im, offset_string, point, font, size, color)


def get_percent_full(goal):
    non_zero = cv2.countNonZero(goal)
    total = goal.shape[0] * goal.shape[1]
    return float(non_zero) / float(total)


def order_points(pts):
    rect = np.zeros((4, 2), dtype="float32")

    s = pts.sum(axis=1)
    rect[0] = pts[np.argmin(s)]
    rect[2] = pts[np.argmax(s)]

    diff = np.diff(pts, axis=1)
    rect[1] = pts[np.argmin(diff)]
    rect[3] = pts[np.argmax(diff)]

    return rect


def four_point_transform(im, pts):
    rect = order_points(pts)
    (tl, tr, br, bl) = pts

    widthA = np.sqrt(((br[0] - bl[0]) ** 2) + ((br[1] - bl[1]) ** 2))
    widthB = np.sqrt(((tr[0] - tl[0]) ** 2) + ((tr[1] - tl[1]) ** 2))
    maxWidth = max(int(widthA), int(widthB))

    heightA = np.sqrt(((tr[0] - br[0]) ** 2) + ((tr[1] - br[1]) ** 2))
    heightB = np.sqrt(((tl[0] - bl[0]) ** 2) + ((tl[1] - bl[1]) ** 2))
    maxHeight = max(int(heightA), int(heightB))

    dst = np.array([
        [0, 0],
        [maxWidth - 1, 0],
        [maxWidth - 1, maxHeight - 1],
        [0, maxHeight - 1]], dtype="float32")

    M = cv2.getPerspectiveTransform(rect, dst)
    warped = cv2.warpPerspective(im, M, (maxWidth, maxHeight))

    return warped
