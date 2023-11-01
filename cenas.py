#!/usr/bin/env python3
import cv2
import numpy as np

# Initialize variables
rectangle = None
drawing = False

def mouse_callback(event, x, y, flags, param):
    global rectangle, drawing

    if event == cv2.EVENT_LBUTTONDOWN:
        rectangle = (x, y, x, y)
        drawing = True

    elif event == cv2.EVENT_MOUSEMOVE and drawing:
        rectangle = (rectangle[0], rectangle[1], x, y)

    elif event == cv2.EVENT_LBUTTONUP:
        drawing = False

def main():
    global rectangle

    # Create a black image
    img = np.zeros((512, 512, 3), dtype=np.uint8)

    cv2.namedWindow("Resize Rectangle")
    cv2.setMouseCallback("Resize Rectangle", mouse_callback)

    while True:
        img_copy = img.copy()

        if rectangle is not None:
            x1, y1, x2, y2 = rectangle
            cv2.rectangle(img_copy, (x1, y1), (x2, y2), (0, 255, 0), 2)

        cv2.imshow("Resize Rectangle", img_copy)

        key = cv2.waitKey(1)
        if key == 27:  # Press 'Esc' to exit
            break

    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
