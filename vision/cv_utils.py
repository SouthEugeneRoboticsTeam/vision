#!/usr/bin/env python

import cv2

from . import args

verbose = args["verbose"]

def process_image(im, lower, upper, min_area):
	# Get image height and width
	height, width = im.shape[:2]

	if verbose:
		print("[Image] width: %d, height: %d" % (width, height))

	# Create mask
	im_mask = cv2.inRange(im, self.lower, self.upper)

	# Get largest blob
	largest = get_largest(im_mask)

	offset_x = 0
	offset_y = 0

	if largest is not False:
		# Get x, y, width, height of goal
		x, y, w, h = cv2.boundingRect(largest)

		# Get area of largest blob
		largest_area = w * h

		if verbose:
			print("[Blob] x: %d, y: %d, width: %d, height: %d, area: %d" % (x, y, w, h, largest))

		if largest_area > min_area:
			# Find center of goal
			center_x = int(0.5 * (x + (x + w)))
			center_y = int(0.5 * (y + (y + h)))

			if verbose:
				print("[Blob] center: (%d, %d)" % (center_x, center_y))

			# Find pixels away from center
			offset_x = int(width/2 - center_x) * -1
			offset_y = int(height/2 - center_y)

			if verbose:
				print("[Blob] offset: (%d, %d)" % (offset_x, offset_y))
	else:
		if verbose:
			print("No largest blob was found")

	return offset_x, offset_y

def draw_images(im, lower, upper, min_area):
	# Get image height and width
	height, width = im.shape[:2]

	if verbose:
		print("[Image] width: %d, height: %d" % (width, height))

	# Create before image
	im_rect = im.copy()

	# Create mask
	im_mask = cv2.inRange(im, lower, upper)

	# Get largest blob
	largest = get_largest(im_mask)

	if largest is not False:
		# Get x, y, width, height of goal
		x, y, w, h = cv2.boundingRect(largest)

		# Get area of largest blob
		largest_area = w * h

		if verbose:
			print("[Blob] x: %d, y: %d, width: %d, height: %d, area: %d" % (x, y, w, h, largest_area))

		if largest_area > min_area:
			# Draw rectangle around goal
			cv2.rectangle(im_rect, (x, y), (x + w, y + h), (255, 0, 0), 2)

			# Find center of goal
			center_x = int(0.5 * (x + (x + w)))
			center_y = int(0.5 * (y + (y + h)))

			if verbose:
				print("[Blob] center: (%d, %d)" % (center_x, center_y))

			# Find pixels away from center
			offset_x = int(width/2 - center_x) * -1
			offset_y = int(height/2 - center_y)

			if verbose:
				print("[Blob] offset: (%d, %d)" % (offset_x, offset_y))

			# Draw point on center of goal
			cv2.circle(im_rect, (center_x, center_y), 2, (255, 0, 0), thickness=3)

			# Put text on screen
			draw_offset(im_rect, offset_x, offset_y, (0, 30), 1, (255, 0, 0))
	else:
		if verbose:
			print("No largest blob was found")

	# Draw crosshair on the screen
	draw_crosshair(im_rect, width, height, (0, 0, 0), 2)

	return im_rect, im_mask

def get_largest(im):
	# Find contours of the shape
	contours, _ = cv2.findContours(im.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

	# Cycle through contours and add area to array
	areas = []
	for c in contours:
		areas.append(cv2.contourArea(c))

	# Sort array of areas by size
	sorted_areas = sorted(zip(areas, contours), key=lambda x: x[0], reverse=True)

	if sorted_areas:
		# Find nth largest using data[n-1][1]
		return sorted_areas[0][1]
	else:
		return False

def draw_crosshair(im, width, height, color, thickness):
	cv2.line(im, (width/2, 0), (width/2, height), color, thickness=thickness)
	cv2.line(im, (0, height/2), (width, height/2), color, thickness=thickness)

def draw_offset(im, offset_x, offset_y, point, size, color):
	font = cv2.FONT_HERSHEY_SIMPLEX
	offset_string = "(" + str(offset_x) + ", " + str(offset_y) + ")"
	cv2.putText(im, offset_string, point, font, size, color)
