import cv2

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
