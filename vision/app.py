#!/usr/bin/env python

import cv2
import numpy as np
import vision.cv_utils as cv_utils
import vision.nt_utils as nt_utils
from imutils.video import WebcamVideoStream
from . import args

verbose = args["verbose"]


class Vision:
	def __init__(self):
		self.args = args

		self.lower = np.array(self.args["lower_color"], dtype="uint8")
		self.upper = np.array(self.args["upper_color"], dtype="uint8")

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

		blob, im_mask = cv_utils.get_blob(im, self.lower, self.upper)
		if blob is not None:
			x, y, w, h = cv2.boundingRect(blob)
			if w * h > self.min_area:
				if verbose:
					print("[Blob] x: %d, y: %d, width: %d, height: %d, area: %d" % (x, y, w, h, w * h))
				im_rect = cv_utils.draw_images(im, x, y, w, h)
				offset_x, offset_y = cv_utils.process_image(im, x, y, w, h)

				nt_utils.put_number("offset_x", offset_x)
				nt_utils.put_number("offset_y", offset_y)
		else:
			if verbose:
				print("No largest blob was found")

		if self.display:
			# Show the images
			if blob is not None:
				cv2.imshow("Original", im_rect)
				cv2.imshow("Mask", im_mask)
			else:
				cv2.imshow("Original", im)

			cv2.waitKey(0)

			cv2.destroyAllWindows()

	def run_video(self):
		camera = WebcamVideoStream(src=0).start()

		if self.verbose:
			print("No image path specified, reading from camera video feed")

		timeout = 0

		while(True):
			# Read image from file
			im = camera.read()

			if im is not None:
				blob, im_mask = cv_utils.get_blob(im, self.lower, self.upper)
				if blob is not None:
					x, y, w, h = cv2.boundingRect(blob)
					if w * h > self.min_area:
						if verbose:
							print("[Blob] x: %d, y: %d, width: %d, height: %d, area: %d" % (x, y, w, h, w * h))
						im_rect = cv_utils.draw_images(im, x, y, w, h)
						offset_x, offset_y = cv_utils.process_image(im, x, y, w, h)

						nt_utils.put_number("offset_x", offset_x)
						nt_utils.put_number("offset_y", offset_y)

						if self.display:
							# Show the images
							cv2.imshow("Original", im_rect)
							cv2.imshow("Mask", im_mask)
				else:
					if verbose:
						print("No largest blob was found")

					if self.display:
						cv2.imshow("Original", im)

				if cv2.waitKey(1) & 0xFF == ord("q"):
					break
			else:
				if (timeout == 0):
					print("No camera detected")

				timeout += 1

				if (timeout > 500):
					print("Camera search timed out")
					break

		cv2.destroyAllWindows()
