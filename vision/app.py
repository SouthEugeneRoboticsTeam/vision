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

		self.min_area = int(self.args["min_area"])

		self.image = self.args["image"]

		self.display = self.args["display"]

	def run(self):
		if self.image is not None:
			self.run_image()
		else:
			self.run_video()

	def run_image(self):
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

		while(True):
			# Read image from file
			(ret, im) = camera.read()

			if ret:
				# check if they wanted to draw images or not
				im_rect, im_mask = cv_utils.draw_images(im, self.lower, self.upper, self.min_area)

				if self.display:
					# Show the images
					cv2.imshow("Original", im_rect)
					cv2.imshow("Mask", im_mask)

					if cv2.waitKey(1) & 0xFF == ord('q'):
						break
			else:
				break

		camera.release()
		cv2.destroyAllWindows()
