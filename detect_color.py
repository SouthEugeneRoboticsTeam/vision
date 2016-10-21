import numpy as np
import argparse
import cv2

# Define arguments
ap = argparse.ArgumentParser()
ap.add_argument("-i", "--image", help="path to image")
args = vars(ap.parse_args())

# Read image from file
im = cv2.imread(args["image"])

# Get image height and width
height, width = im.shape[:2]

# Define lower and upper thresholds (RGB)
lower = [65, 215, 5]
upper = [125, 255, 75]

# Make the thresholds numpy arrays
lower = np.array(lower, dtype="uint8")
upper = np.array(upper, dtype="uint8")

# Create before image
im_rect = im.copy()

# Create mask
im_mask = cv2.inRange(im, lower, upper)

# Find contours of the shape
contours, _ = cv2.findContours(im_mask.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

# Cycle through contours and add area to array
areas = []
for c in contours:
    areas.append(cv2.contourArea(c))

# Sort array of areas by size
sorted_areas = sorted(zip(areas, contours), key=lambda x: x[0], reverse=True)

# Find nth largest using data[n-1][1]
largest = sorted_areas[0][1]

# Get x, y, width, height of goal
x, y, w, h = cv2.boundingRect(largest)

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

# Draw lines on the screen
cv2.line(im_rect, (width/2, 0), (width/2, height), (0, 0, 0), thickness=2)
cv2.line(im_rect, (0, height/2), (width, height/2), (0, 0, 0), thickness=2)

# Put text on screen
font = cv2.FONT_HERSHEY_SIMPLEX
offset_string = "(" + str(offset_x) + ", " + str(offset_y) + ")"
cv2.putText(im_rect, offset_string, (0, 30), font, 1, (255, 0, 0))

print (offset_x, offset_y)

# Show the images
cv2.imshow("Original", im_rect)
cv2.imshow("Mask", im_mask)
cv2.waitKey(0)
