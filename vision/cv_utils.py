#!/usr/bin/env python

import json
import math

import cv2
import imutils
import numpy as np

from . import args

verbose = args["verbose"]
display = args["display"]
camera_file = args["camera"]

# Points comprising 3D model of target
full_model_points = np.array([
    (-5.938, 2.938, 0.0),
    (-4.063, 2.375, 0.0),
    (-5.438, -2.938, 0.0),
    (-7.375, -2.500, 0.0),

    (3.938, 2.375, 0.0),
    (5.875, 2.875, 0.0),
    (7.313, -2.500, 0.0),
    (5.375, -2.938, 0.0),
])

with open(camera_file) as f:
    data = json.load(f)

    camera_matrix = np.array(data["camera_matrix"], dtype="double")
    dist_coeffs = np.array(data["distortion"], dtype="double")


def process_image(im, goal, blobs):
    right_target = goal[0]
    left_target = goal[1]

    right_blob = blobs[0]
    left_blob = blobs[1]

    right_area = cv2.contourArea(right_blob)
    left_area = cv2.contourArea(left_blob)

    # Find center of goal
    left_center_x = left_target[0][0]
    left_center_y = left_target[0][1]
    right_center_x = right_target[0][0]
    right_center_y = right_target[0][1]

    center_x = (left_center_x + right_center_x) / 2
    center_y = (left_center_y + right_center_y) / 2

    model_points = full_model_points

    right_peri = cv2.arcLength(right_blob, True)
    right_approx = cv2.approxPolyDP(right_blob, 0.01 * right_peri, True)

    left_peri = cv2.arcLength(left_blob, True)
    left_approx = cv2.approxPolyDP(left_blob, 0.01 * left_peri, True)

    left_box_points = order_points(np.int0(cv2.boxPoints(left_target))).tolist()
    right_box_points = order_points(np.int0(cv2.boxPoints(right_target))).tolist()

    left_points = order_points(np.int0([x[0] for x in left_approx])).tolist()
    right_points = order_points(np.int0([x[0] for x in right_approx])).tolist()

    sorted_left_points, delete_left = filter_points_to_box(left_points, left_box_points, left_area)
    sorted_right_points, delete_right = filter_points_to_box(right_points, right_box_points, right_area, offset=4)
    delete_model_points = delete_left + delete_right

    model_points = np.delete(model_points, delete_model_points, 0)
    image_points = np.array(sorted_left_points + sorted_right_points)

    # Calculate rotation vector and translation vector
    (ret, rvec, tvec) = cv2.solvePnP(model_points, image_points, camera_matrix, dist_coeffs)

    distance, robot_angle, target_angle = compute_output_values(rvec, tvec)

    x_distance = np.sin(robot_angle) * distance
    y_distance = np.cos(robot_angle) * distance

    centroid = (int(center_x), int(center_y))

    if verbose:
        print(model_points, image_points)
        print(distance, robot_angle, target_angle, rvec)
        print("X: {}, Y: {}".format(x_distance, y_distance))

    if display:
        (endpoint2D, jacobian) = cv2.projectPoints(np.array([(0.0, 0.0, 6.0)]), rvec, tvec, camera_matrix, dist_coeffs)

        cv2.circle(im, (int(left_center_x), int(left_center_y)), 3, (0, 0, 255), -1)
        cv2.circle(im, (int(right_center_x), int(right_center_y)), 3, (0, 0, 255), -1)

        for p in image_points:
            cv2.circle(im, (int(p[0]), int(p[1])), 2, (0, 0, 255), -1)

        p2 = (int(endpoint2D[0][0][0]), int(endpoint2D[0][0][1]))

        try:
            cv2.line(im, centroid, p2, (0, 255, 255), 2)
        except OverflowError:
            pass

    return np.rad2deg(robot_angle), np.rad2deg(target_angle), x_distance, y_distance, distance, centroid


def filter_points_to_box(real_points, box_points, area, offset=0):
    filtered_points = []
    delete_model_points = []

    if len(real_points) == len(box_points):
        for i, points in enumerate(zip(real_points, box_points)):
            point, box_point = points
            dist = (point[0] - box_point[0]) ** 2.0 + (point[1] - box_point[1]) ** 2.0
            ratio = dist / area

            if ratio > 0.04:
                delete_model_points.append(offset + i)
            else:
                filtered_points.append(point)

    return filtered_points, delete_model_points


def draw_images(im, rect, box):
    # Create before image
    im_rect = im.copy()

    # Draw rectangle around goal
    cv2.drawContours(im_rect, [box], 0, (40, 225, 245), 2)

    # Find center of goal
    center_x = int(rect[0][0])
    center_y = int(rect[0][1])

    # Draw point on center of goal
    cv2.circle(im_rect, (center_x, center_y), 2, (255, 0, 0), -1)

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
