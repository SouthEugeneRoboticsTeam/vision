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
		self.max_area = int(self.args["max_area"])

		self.image = self.args["image"]

		self.display = self.args["display"]

		self.verbose = self.args["verbose"]

		self.source = self.args["sources"]

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
			x1, y1, w1, h1 = cv2.boundingRect(blob[0])
			x2, y2, w2, h2 = cv2.boundingRect(blob[1])

			if w1 * h1 > self.min_area and w2 * h2 > self.min_area:
				if verbose:
					print("[Blob 1] x: %d, y: %d, width: %d, height: %d, area: %d" % (x1, y1, w1, h1, w1 * h1))
					print("[Blob 2] x: %d, y: %d, width: %d, height: %d, area: %d" % (x2, y2, w2, h2, w2 * h2))

				im_rect = cv_utils.draw_images(im, x1, y1, w1, h1)

				offset_x, offset_y = cv_utils.process_image(im, x1 * x2 / 2, y1 * y2 / 2, w1 * w2 / 2, h1 * h2 / 2)

				print(offset_x)
				print(offset_y)

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
		cameraFront = WebcamVideoStream(src=self.source[0]).start()
		cameraRear = WebcamVideoStream(src=self.source[1]).start()

		if self.verbose:
			print("No image path specified, reading from camera video feed")

		timeout = 0

		while(True):
			if nt_utils.get_boolean("front_camera"):
				im = cameraFront.read()
			else:
				im = cameraRear.read()

			im = cv2.resize(im, (600, 480), 0, 0)

			if im is not None:
				blob, im_mask = cv_utils.get_blob(im, self.lower, self.upper)
				if blob is not None:
					x1, y1, w1, h1 = cv2.boundingRect(blob[0])
					x2, y2, w2, h2 = cv2.boundingRect(blob[1])
					if w1 * h1 > self.min_area and w2 * h2 > self.min_area and w1 * h1 > self.max_area and w2 * h2 > self.max_area:
						if verbose:
							print("[Blob] x: %d, y: %d, width: %d, height: %d, area: %d" % (x1, y1, w1, h1, w1 * h1))

						offset_x, offset_y = cv_utils.process_image(im, x1, y1, w1, h1, x2, y2, w2, h2)

						nt_utils.put_number("offset_x", offset_x)
						nt_utils.put_number("offset_y", offset_y)

						# Draw image details
						im = cv_utils.draw_images(im, x1, y1, w1, h1)
						im = cv_utils.draw_images(im, x2, y2, w2, h2)

					if self.display:
						# Show the images
						cv2.imshow("Original", im)
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
