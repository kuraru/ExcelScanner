import cv2

# Read an image from file
image = cv2.imread("20231009-181355-189-01.jpg")

# Display the image in a window
cv2.imshow('Image', image)

# Wait for a key press and close the window
cv2.waitKey(0)
cv2.destroyAllWindows()

