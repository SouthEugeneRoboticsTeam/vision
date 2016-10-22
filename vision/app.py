#!/usr/bin/python

import numpy as np
import utils
import cv_utils
import cv2

class Vision:
	def __init__(self):
		self.args = utils.get_args()

		self.lower = np.array(self.args["lower_rgb"], dtype="uint8")
		self.upper = np.array(self.args["upper_rgb"], dtype="uint8")

		self.image = self.args["image"]

	def run(self):
		if self.image is not None:
			self.run_image()
		else:
			self.run_video()

	def process_image(self, im):
		# Get image height and width
		height, width = im.shape[:2]

		# Create before image
		im_rect = im.copy()

		# Create mask
		im_mask = cv2.inRange(im, self.lower, self.upper)

		# Get largest blob
		largest = cv_utils.get_largest(im_mask)

		if largest is not False:
			# Get x, y, width, height of goal
			x, y, w, h = cv2.boundingRect(largest)

			# Get area of largest blob
			largest_area = w * h

			if largest_area > self.args["min_area"]:
				# Draw rectangle around goal
				cv2.rectangle(im_rect, (x, y), (x + w, y + h), (255, 0, 0), 2)

				# Find center of goal
				center_x = int(0.5 * (x + (x + w)))
				center_y = int(0.5 * (y + (y + h)))

				# Find pixels away from center
				offset_x = int(width/2 - center_x) * -1
				offset_y = int(height/2 - center_y)

				# Draw point on center of goal
				cv2.circle(im_rect, (center_x, center_y), 2, (255, 0, 0), thickness=3)

				# Put text on screen
				cv_utils.draw_offset(im_rect, offset_x, offset_y, (0, 30), 1, (255, 0, 0))

		# Draw crosshair on the screen
		cv_utils.draw_crosshair(im_rect, width, height, (0, 0, 0), 2)

		return im_rect, im_mask

	def run_image(self):
		im = cv2.imread(self.image)

		im_rect, im_mask = self.process_image(im)

		# Show the images
		cv2.imshow("Original", im_rect)
		cv2.imshow("Mask", im_mask)

		cv2.waitKey(0)

		cv2.destroyAllWindows()

	def run_video(self):
		camera = cv2.VideoCapture(0)

		while(True):
			# Read image from file
			(ret, im) = camera.read()

			if ret:
				im_rect, im_mask = self.process_image(im)

				# Show the images
				cv2.imshow("Original", im_rect)
				cv2.imshow("Mask", im_mask)

				if cv2.waitKey(1) & 0xFF == ord('q'):
					break
			else:
				break

		self.camera.release()
		cv2.destroyAllWindows()
