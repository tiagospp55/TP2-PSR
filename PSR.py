#!/usr/bin/env python3
import cv2
import json
import argparse
import numpy as np
from time import ctime
from colorama import Fore
from functools import partial 

def mouseCallback(event, x, y, flags, *userdata, image_canvas, drawing_data):

    if event == cv2.EVENT_LBUTTONDOWN:
        drawing_data['pencil_down'] = True
        print(Fore.BLUE + 'pencil_down set to True' + Fore.RESET)
        
    elif event == cv2.EVENT_LBUTTONUP: 
        drawing_data['pencil_down'] = False
        print(Fore.RED + 'pencil_down released' + Fore.RESET)

    if drawing_data['pencil_down'] == True:
        # cv2.circle(image_rgb, (x, y), 3, (255,255,255), -1)
        cv2.line(image_canvas, (drawing_data['previous_x'], drawing_data['previous_y']), (x,y), drawing_data['color'], drawing_data['size']) 

    drawing_data['previous_x'] = x
    drawing_data['previous_y'] = y

def onTrackbar(min_B, max_B, min_G, max_G, min_R, max_R, image):
    min_B = cv2.getTrackbarPos('min B/H', 'Camera')
    max_B = cv2.getTrackbarPos('max B/H', 'Camera')
    min_G = cv2.getTrackbarPos('min G/S', 'Camera')
    max_G = cv2.getTrackbarPos('max G/S', 'Camera')
    min_R = cv2.getTrackbarPos('min R/V', 'Camera')
    max_R = cv2.getTrackbarPos('max R/V', 'Camera')

    mask = cv2.inRange(image, (min_B,min_G,min_R), (max_B,max_G,max_R))
    cv2.imshow('Camera', mask)

    return mask

def main():
    parser = argparse.ArgumentParser(description='Definition of ' + Fore.BLUE + 'test ' + Fore.RESET + 'mode')
    parser.add_argument('-j', '--json', type=str, required=True, help='Full path to json file.')
    args = vars(parser.parse_args())

    image_canvas = np.ones((400,600,3), dtype=np.uint8) * 255

    drawing_data = {'pencil_down': False, 'previous_x': 0, 'previous_y': 0, 'color': (255,255,255), 'size': 1}

    # initial setup
    capture = cv2.VideoCapture(0)

    cv2.namedWindow('Canvas')
    cv2.namedWindow('Camera', cv2.WINDOW_AUTOSIZE)

    _, image = capture.read()  # get an image from the camera

    if args['json']:
        file_name = args['json']

        openFile = open(file_name)

        d = json.load(openFile)

        print(d)

        openFile.close()

    cv2.createTrackbar('min B/H', 'Camera', 0, 255, 
                       lambda x : onTrackbar(x,0,0,0,0,0,image))

    cv2.createTrackbar('max B/H', 'Camera', 0, 255,
                       lambda x : onTrackbar(0,x,0,0,0,0,image))
    
    cv2.createTrackbar('min G/S', 'Camera', 0, 255, 
                       lambda x : onTrackbar(0,0,x,0,0,0,image))
    
    cv2.createTrackbar('max G/S', 'Camera', 0, 255,  
                       lambda x : onTrackbar(0,0,0,x,0,0,image))
    
    cv2.createTrackbar('min R/V', 'Camera', 0, 255, 
                       lambda x : onTrackbar(0,0,0,0,x,0,image))
    
    cv2.createTrackbar('max R/V', 'Camera', 0, 255, 
                       lambda x : onTrackbar(0,0,0,0,0,x,image))

    cv2.setTrackbarPos('min B/H', 'Camera',d['limits']['B']['min'])
    cv2.setTrackbarPos('max B/H', 'Camera',d['limits']['B']['max'])
    cv2.setTrackbarPos('min G/S', 'Camera',d['limits']['G']['min'])
    cv2.setTrackbarPos('max G/S', 'Camera',d['limits']['G']['max'])
    cv2.setTrackbarPos('min R/V', 'Camera',d['limits']['R']['min'])
    cv2.setTrackbarPos('max R/V', 'Camera',d['limits']['R']['max'])

    while True:

        _, image = capture.read()

        cv2.setMouseCallback("Canvas", partial(mouseCallback, image_canvas=image_canvas, drawing_data=drawing_data))

        onTrackbar(d['limits']['B']['min'], d['limits']['B']['max'], 
                   d['limits']['G']['min'], d['limits']['G']['max'], 
                   d['limits']['R']['min'], d['limits']['R']['max'], 
                    image)

        cv2.imshow('Canvas', image_canvas)

        cv2.imshow('Original', image)

        key = cv2.waitKey(25)

        if key == ord('j'):

            d = {'limits': {
                'B': {'max': cv2.getTrackbarPos('max B/H', 'Camera'), 'min': cv2.getTrackbarPos('min B/H', 'Camera')},
                'G': {'max': cv2.getTrackbarPos('max G/S', 'Camera'), 'min': cv2.getTrackbarPos('min G/S', 'Camera')},
                'R': {'max': cv2.getTrackbarPos('max R/V', 'Camera'), 'min': cv2.getTrackbarPos('min R/V', 'Camera')}}}

            print(d)

            d_json = json.dumps(d)

            print(d_json)

            file_name = 'limits.json'

            openFile = open(file_name, "w")

            openFile.write(d_json)

            openFile.close()

        elif key == ord('q'):
            break

        elif key == ord('r'): # red color for pencil
            print('Setting pencil to red color')
            # TODO how to set the red color?
            drawing_data['color'] = (0,0,255)

        elif key == ord('g'): # red color for pencil
            print('Setting pencil to green color')
            # TODO how to set the red color?
            drawing_data['color'] = (0,255,0)

        elif key == ord('b'): # red color for pencil
            print('Setting pencil to blue color')
            # TODO how to set the red color?
            drawing_data['color'] = (255,0,0)

        elif key == ord('-'): # Decrease pencil size
            print('Decreasing pencil size')
            # TODO how to set smaller pencil size?
            if drawing_data['size'] == 1:
                print("Minimum size possible")
            elif drawing_data['size'] >= 1:
                drawing_data['size'] -= 1
                print("Decrease to " + str(drawing_data['size']))

        elif key == ord('+'): # Increase pencil size
            print('Increasing pencil size')
            # TODO how to set bigger pencil size?
            if drawing_data['size'] == 50:
                print("Max size possible")
            elif drawing_data['size'] < 50:
                drawing_data['size'] += 1
                print("Increase to " + str(drawing_data['size']))

        elif key == ord('c'): # Clear canvas
            print('Clear canvas')
            # TODO how to clear canvas?
            image_canvas = np.ones((400,600,3), dtype=np.uint8) * 255

        elif key == ord('w'): # Save canvas
            print('Saving image')
            # TODO how to save canvas?
            new_name = ctime()
            nameList = new_name.split()
            cv2.imwrite('drawing_' + 
                        nameList[0] + '_' + 
                        nameList[1] + '_' + 
                        nameList[2] + '_' + 
                        nameList[3] + '_' + 
                        nameList[4] + '.png', image_canvas)

if __name__ == '__main__':
    main()