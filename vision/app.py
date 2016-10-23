#!/usr/bin/env python

import numpy as np
import vision.cv_utils as cv_utils
import cv2

from . import args

class Vision:
	def __init__(self):
		self.args = args

		self.lower = np.array(self.args["lower_rgb"], dtype="uint8")
		self.upper = np.array(self.args["upper_rgb"], dtype="uint8")

		self.min_area = int(self.args["min_area"])

		self.image = self.args["image"]

		self.display = self.args["display"]

		self.verbose = self.args["verbose"]

		if self.verbose:
			print(self.args)

	def run(self):
		if self.image is not None:
			self.run_image()
		else:
			self.run_video()

	def run_image(self):
		if self.verbose:
			print("Image path specified, reading from %s" % self.image)

		im = cv2.imread(self.image)

		im_rect, im_mask = cv_utils.draw_images(im, self.lower, self.upper, self.min_area)

		if self.display:
			# Show the images
			cv2.imshow("Original", im_rect)
			cv2.imshow("Mask", im_mask)

			cv2.waitKey(0)

			cv2.destroyAllWindows()

	def run_video(self):
		camera = cv2.VideoCapture(0)

		if self.verbose:
			print("No image path specified, reading from camera video feed")

		timeout = 0

		while(True):
			# Read image from file
			(ret, im) = camera.read()

			if ret:
				im_rect, im_mask = cv_utils.draw_images(im, self.lower, self.upper, self.min_area)

				if self.display:
					# Show the images
					cv2.imshow("Original", im_rect)
					cv2.imshow("Mask", im_mask)

					if cv2.waitKey(1) & 0xFF == ord('q'):
						break
			else:
				if (timeout == 0):
					print("No camera detected")

				timeout += 1

				if (timeout > 500):
					print("Camera search timed out")
					break

		camera.release()
		cv2.destroyAllWindows()
