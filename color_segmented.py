#!/usr/bin/env python3

#------------------------------------------
#   Libraries
#------------------------------------------

import cv2
import json
import argparse
import numpy as np
from time import ctime
from colorama import Fore

#------------------------------------------
#   Trackbar manager
#------------------------------------------

def onTrackbar(min_B, max_B, min_G, max_G, min_R, max_R, image):

    """
    Agrs:
        min_B : 0 to 255
        max_B : 0 to 255
        min_G : 0 to 255
        max_G : 0 to 255
        min_R : 0 to 255
        max_R : 0 to 255
        image : Captured image

    Return:
        mask : Alter image of the var image
    """

    # Saves the value of every parameter
    min_B = cv2.getTrackbarPos('min B/H', 'Camera')
    max_B = cv2.getTrackbarPos('max B/H', 'Camera')
    min_G = cv2.getTrackbarPos('min G/S', 'Camera')
    max_G = cv2.getTrackbarPos('max G/S', 'Camera')
    min_R = cv2.getTrackbarPos('min R/V', 'Camera')
    max_R = cv2.getTrackbarPos('max R/V', 'Camera')

    # Doing the mask with image captured by the camera 
    mask = cv2.inRange(image, (min_B,min_G,min_R), (max_B,max_G,max_R))
    # Show filtered image
    cv2.imshow('Camera', mask)

    # Return the value of the mask
    return mask

#------------------------------------------
#   Main Cycle
#------------------------------------------

def main():

    #------------------------------------------
    #   Initialzation
    #------------------------------------------

    # Flag reset that indicate that the file was saved before exit the program
    fileSaved_flag = False

    # Define description of help
    parser = argparse.ArgumentParser(description='Definition of ' + Fore.BLUE + 'test ' + Fore.RESET + 'mode')
    # Create argument that wants a file json to read
    parser.add_argument('-j', '--json', type=str, required=True, help='Full path to json file.')
    # Create a dictionary of the arguments
    args = vars(parser.parse_args())

    # Create a blank canvas 
    image_canvas = np.ones((400,600,3), dtype=np.uint8) * 255

    # Get image for camera
    capture = cv2.VideoCapture(0)

    # Create void windows 
    cv2.namedWindow('Canvas')
    cv2.namedWindow('Camera', cv2.WINDOW_AUTOSIZE)

    # Get an image from the camera
    _, image = capture.read()

    # Reads the json file that the user choose to get the parameters for the trackbars
    if args['json']:
        file_name = args['json']

        openFile = open(file_name)

        d = json.load(openFile)

        print(d)

        openFile.close()

    #------------------------------------------
    #   Execution
    #------------------------------------------

    # Create trackbars to transfers each value to the mask
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

    # Set the value of each trackbar to the value of read on the json file
    cv2.setTrackbarPos('min B/H', 'Camera',d['limits']['B']['min'])
    cv2.setTrackbarPos('max B/H', 'Camera',d['limits']['B']['max'])
    cv2.setTrackbarPos('min G/S', 'Camera',d['limits']['G']['min'])
    cv2.setTrackbarPos('max G/S', 'Camera',d['limits']['G']['max'])
    cv2.setTrackbarPos('min R/V', 'Camera',d['limits']['R']['min'])
    cv2.setTrackbarPos('max R/V', 'Camera',d['limits']['R']['max'])

    #------------------------------------------
    #   Visualization
    #------------------------------------------

    while True:

        # Get an image from the camera
        _, image = capture.read()

        # Transfer value from the file to the function onTrackbar
        onTrackbar(d['limits']['B']['min'], d['limits']['B']['max'], 
                   d['limits']['G']['min'], d['limits']['G']['max'], 
                   d['limits']['R']['min'], d['limits']['R']['max'], 
                    image)

        # Show canvas that serves to draw
        cv2.imshow('Canvas', image_canvas)

        # Show original image that is being filtered
        cv2.imshow('Original', image)

        # Save value for the pressed key ----- Image refresh 25 ms
        key = cv2.waitKey(1)

        # By pressing the j key program will save the parameters of the filter
        if key == ord('j'):

            # Struch the data of the trackbars parameters
            d = {'limits': {
                'B': {'max': cv2.getTrackbarPos('max B/H', 'Camera'), 'min': cv2.getTrackbarPos('min B/H', 'Camera')},
                'G': {'max': cv2.getTrackbarPos('max G/S', 'Camera'), 'min': cv2.getTrackbarPos('min G/S', 'Camera')},
                'R': {'max': cv2.getTrackbarPos('max R/V', 'Camera'), 'min': cv2.getTrackbarPos('min R/V', 'Camera')}}}

            d_json = json.dumps(d)

            # Shows the user the aspect of the file saved
            print(d_json)

            file_name = 'limits.json'

            openFile = open(file_name, "w")

            openFile.write(d_json)

            openFile.close()

            # Flag to indicate that the file was saved before exit the program
            fileSaved_flag = True

            print("File " + args['json'] + " as been saved")
            print(Fore.GREEN + "Now you can exit the program safely!!" + Fore.RESET)

        #------------------------------------------
        #   Termination
        #------------------------------------------

        # By pressing the q key will exit the user from the program
        elif key == ord('q'):
            # If the user doesn't save the file the program will warn the user about it and exit
            if fileSaved_flag == False:
                print(Fore.RED + "Just to remind you will exit without saving the file that contain the paremeters of the trackbars" + Fore.RESET)
            break

if __name__ == '__main__':
    main()