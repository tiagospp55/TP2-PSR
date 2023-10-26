import cv2
import numpy as np

# Load an image, preferably in grayscale
image = cv2.imread('../MRSI/VC/Aula1/lena.jpg', cv2.IMREAD_COLOR)

# Threshold the image to create a binary image
ret, binary_image = cv2.threshold(image, 0, 150, cv2.THRESH_BINARY)

# Use connectedComponentsWithStats to label connected components
num_labels, labels, stats, centroids = cv2.connectedComponentsWithStats(binary_image, connectivity=8)

# num_labels: Number of connected components found in the image.
# labels: A labeled image, where each pixel is assigned a label (0 for background).
# stats: A 2D array containing statistics for each connected component.
# centroids: A 2D array containing the (x, y) coordinates of the centroids of each component.
print(num_labels)
print(labels[0])


# Iterate through the connected components and their statistics
for label in range(1, num_labels):
    left, top, width, height, area = stats[label]
    centroid_x, centroid_y = centroids[label]
    #print all data
    print(left, top, width, height, area, centroid_x, centroid_y)


    # You can perform actions based on the statistics of each component, for example, drawing a bounding box
    recctangle = cv2.rectangle(image, (left, top), (left + width, top + height), (0, 255, 0), 2)



image1 = cv2.add(image, recctangle)
    
# Display the image with bounding boxes around connected components
cv2.imshow("Image", image)
cv2.imshow("binary", binary_image)
cv2.imshow('Connected Components', image1)
cv2.waitKey(0)
cv2.destroyAllWindows()
