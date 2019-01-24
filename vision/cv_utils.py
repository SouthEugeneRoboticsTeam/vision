#!/usr/bin/env python

import math

import cv2
import imutils
import numpy as np

from . import args

verbose = args["verbose"]
horizontal_fov = args["horizontal_fov"]
vertical_fov = args["vertical_fov"]
target_width = args["target_width"]
target_height = args["target_height"]
calculate_distances = args["calculate_distances"]
display = args["display"]

# Points comprising 3D model of target
model_points = np.array([
    (-5.938, 2.938, 0.0),
    (-4.063, 2.375, 0.0),
    (-5.438, -2.938, 0.0),
    (-7.375, -2.500, 0.0),

    (3.938, 2.375, 0.0),
    (5.875, 2.875, 0.0),
    (7.313, -2.500, 0.0),
    (5.375, -2.938, 0.0),
])


def process_image(im, goal):
    # Calculated camera matrix
    camera_matrix = np.array(
        [[670.54273808, 0., 347.71623038],
         [0., 678.11163899, 238.40313974],
         [0., 0., 1.]], dtype="double"
    )

    # Distortion coefficients, from checkerboard vision
    dist_coeffs = np.array([2.06743428e-01, -1.65831760e+00, 1.06922781e-03, 1.03675715e-02, 3.33870248e+00])
    # dist_coeffs = np.zeros((4, 1))

    right_target = goal[0]
    left_target = goal[1]

    # Find center of goal
    left_center_x = left_target[0][0]
    left_center_y = left_target[0][1]
    right_center_x = right_target[0][0]
    right_center_y = right_target[0][1]

    center_x = (left_center_x + right_center_x) / 2
    center_y = (left_center_y + right_center_y) / 2

    left_points = order_points(np.int0(cv2.boxPoints(left_target))).tolist()
    right_points = order_points(np.int0(cv2.boxPoints(right_target))).tolist()

    image_points = np.array(left_points + right_points)

    # Calculate rotation vector and translation vector
    (ret, rvec, tvec) = cv2.solvePnP(model_points, image_points, camera_matrix, dist_coeffs)

    (endpoint2D, jacobian) = cv2.projectPoints(np.array([(0.0, 0.0, 6.0)]), rvec, tvec, camera_matrix, dist_coeffs)

    distance, robot_angle, target_angle = compute_output_values(rvec, tvec)

    if verbose:
        print(distance, robot_angle, target_angle, rvec)
        print("X: {}, Y: {}".format(np.sin(robot_angle) * distance, np.cos(robot_angle) * distance))

    if display:
        cv2.circle(im, (int(left_center_x), int(left_center_y)), 3, (0, 0, 255), -1)
        cv2.circle(im, (int(right_center_x), int(right_center_y)), 3, (0, 0, 255), -1)

        for p in image_points:
            cv2.circle(im, (int(p[0]), int(p[1])), 3, (0, 0, 255), -1)

        p1 = (int(center_x), int(center_y))
        p2 = (int(endpoint2D[0][0][0]), int(endpoint2D[0][0][1]))

        try:
            cv2.line(im, p1, p2, (255, 0, 0), 2)
        except OverflowError:
            pass

    return robot_angle, target_angle, distance, tvec, rvec


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


def get_blobs(im, lower, upper):
    # Finds a blob, if one exists

    # Create mask of green
    mask = cv2.inRange(im, lower, upper)

    # Get largest blob
    blobs = get_all(mask)

    if blobs is not None:
        return blobs, mask
    else:
        return [], None


def get_largest(im, n):
    # Find contours of the shape
    contours = get_all(im)

    # Create array of contour areas
    areas = [cv2.contourArea(contour) for contour in contours]

    # Sort array of areas by size
    sorted_areas = sorted(zip(areas, contours), key=lambda x: x[0], reverse=True)

    if sorted_areas and len(sorted_areas) >= n:
        # Find nth largest
        return sorted_areas[n - 1][1]
    else:
        return None


def get_all(im):
    # Find contours of the shape
    contours = cv2.findContours(im.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    return imutils.grab_contours(contours)


def draw_offset(im, offset_x, offset_y, point, size, color):
    font = cv2.FONT_HERSHEY_SIMPLEX
    offset_string = "(" + str(offset_x) + ", " + str(offset_y) + ")"
    cv2.putText(im, offset_string, point, font, size, color)


def get_percent_full(goal):
    non_zero = cv2.countNonZero(goal)
    total = goal.shape[0] * goal.shape[1]
    return float(non_zero) / float(total)


def compute_output_values(rvec, tvec):
    x = tvec[0][0]
    z = tvec[2][0]
    # distance in the horizontal plane between camera and target
    distance = math.sqrt(x ** 2 + z ** 2)
    # horizontal angle between camera center line and target
    angle1 = math.atan2(x, z)
    rot, _ = cv2.Rodrigues(rvec)
    rot_inv = rot.transpose()
    pzero_world = np.matmul(rot_inv, -tvec)
    angle2 = math.atan2(pzero_world[0][0], pzero_world[2][0])
    return distance, angle1, angle2


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
