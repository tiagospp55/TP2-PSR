#!/usr/bin/env python3

#------------------------------------------
#   Libraries
#------------------------------------------

from functools import partial
import cv2
import json
from colorama import Fore

#--------------------------------------------------
#   Check if the value of trackbars are diferrent 
#--------------------------------------------------

def checkValues(dictValuesNew, dictValuesOld):

    """
    Args:
        dictValuesNew   : 'limits': {'B': {'max': -, 'min': -},
                                     'G': {'max': -, 'min': -},
                                     'R': {'max': -, 'min': -}
        dictValuesOld   : {'B': {'max': -, 'min': -},
                           'G': {'max': -, 'min': -},
                           'R': {'max': -, 'min': -}}
    Ret :
        different   : True or False
    """

    different = False

    # Compare the value if they different
    if  ((dictValuesOld['B']['min'] == dictValuesNew['limits']['B']['min'])  and
        (dictValuesOld['B']['max']  == dictValuesNew['limits']['B']['max'])  and
        (dictValuesOld['G']['min']  == dictValuesNew['limits']['G']['min'])  and
        (dictValuesOld['G']['max']  == dictValuesNew['limits']['G']['max'])  and
        (dictValuesOld['R']['min']  == dictValuesNew['limits']['R']['min'])  and
        (dictValuesOld['R']['max']  == dictValuesNew['limits']['R']['max'])):
        # Values are not different
        different = False
    else:
        # Values are not different
        different = True

    # Passa the new value to old value to compare on the next iteration
    dictValuesOld['B']['min'] = dictValuesNew['limits']['B']['min']
    dictValuesOld['B']['max'] = dictValuesNew['limits']['B']['max']
    dictValuesOld['G']['min'] = dictValuesNew['limits']['G']['min']
    dictValuesOld['G']['max'] = dictValuesNew['limits']['G']['max']
    dictValuesOld['R']['min'] = dictValuesNew['limits']['R']['min']
    dictValuesOld['R']['max'] = dictValuesNew['limits']['R']['max']

    return different

#------------------------------------------
#   onMouse event pre-set trackbar values 
#------------------------------------------

def onMousePreSetTrackbar(event, x, y, flags, param, colorBGR):

    """
    Args:
        event       : functions of the mouse
        x           : Coordinate of x of the mouse
        y           : Coordinate of y of the mouse
        flags       : Not being used
        param       : Not being used
        colorBGR    : Image
    """

    # Waits for a left mouse click event
    if event == cv2.EVENT_LBUTTONDOWN:
        # Gets the value of each channel 
        pixel_color_blue = colorBGR[x,y,0]
        pixel_color_green = colorBGR[x,y,1]
        pixel_color_red = colorBGR[x,y,2]

        # Sets the value of the pixel that as been pressed by the mouse
        cv2.setTrackbarPos('min B', 'Camera', pixel_color_blue)
        cv2.setTrackbarPos('max B', 'Camera', pixel_color_blue)
        cv2.setTrackbarPos('min G', 'Camera', pixel_color_green)
        cv2.setTrackbarPos('max G', 'Camera', pixel_color_green)
        cv2.setTrackbarPos('min R', 'Camera', pixel_color_red)
        cv2.setTrackbarPos('max R', 'Camera', pixel_color_red)

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
    """

    # Saves the value of every parameter
    min_B = cv2.getTrackbarPos('min B', 'Camera')
    max_B = cv2.getTrackbarPos('max B', 'Camera')
    min_G = cv2.getTrackbarPos('min G', 'Camera')
    max_G = cv2.getTrackbarPos('max G', 'Camera')
    min_R = cv2.getTrackbarPos('min R', 'Camera')
    max_R = cv2.getTrackbarPos('max R', 'Camera')

    # Doing the mask with image captured by the camera 
    mask = cv2.inRange(image, (min_B,min_G,min_R), (max_B,max_G,max_R))
    # Show filtered image
    cv2.imshow('Camera', mask)

#------------------------------------------
#   Main Cycle
#------------------------------------------

def main():

    #------------------------------------------
    #   Initialzation
    #------------------------------------------

    print("This program serves to save parameters that will be used to detect colors")
    print("The comands of the program are the follow ----> j (to save) and q (to quit the program)")

    # Dictionary that will contain the parameters for the video filter
    d = {'limits': {'B': {'max': 0, 'min': 0},
                    'G': {'max': 0, 'min': 0},
                    'R': {'max': 0, 'min': 0}}}

    dataState = {'B': {'max': 0, 'min': 0},
                 'G': {'max': 0, 'min': 0},
                 'R': {'max': 0, 'min': 0}}

    # Var that dictate what will happen if the user decides to exit the program without saving the file.json
    decisionWord = ""

    # Get image for camera
    capture = cv2.VideoCapture(0)

    # Create void windows
    cv2.namedWindow('Camera', cv2.WINDOW_AUTOSIZE)

    # Get an image from the camera
    _, image = capture.read()

    #------------------------------------------
    #   Execution
    #------------------------------------------

    # Create trackbars to transfers each value to the mask
    cv2.createTrackbar('min B', 'Camera', 0, 255, 
                       lambda x : onTrackbar(x,0,0,0,0,0,image))

    cv2.createTrackbar('max B', 'Camera', 0, 255,
                       lambda x : onTrackbar(0,x,0,0,0,0,image))
    
    cv2.createTrackbar('min G', 'Camera', 0, 255, 
                       lambda x : onTrackbar(0,0,x,0,0,0,image))
    
    cv2.createTrackbar('max G', 'Camera', 0, 255,  
                       lambda x : onTrackbar(0,0,0,x,0,0,image))
    
    cv2.createTrackbar('min R', 'Camera', 0, 255, 
                       lambda x : onTrackbar(0,0,0,0,x,0,image))
    
    cv2.createTrackbar('max R', 'Camera', 0, 255, 
                       lambda x : onTrackbar(0,0,0,0,0,x,image))

    #------------------------------------------
    #   Visualization
    #------------------------------------------

    while True:

        # Get an image from the camera
        _, image = capture.read()

        # Transfer value from the file to the function onTrackbar
        onTrackbar(0, 0, 0, 0, 0, 0, image)

        # Struch the data of the trackbars parameters
        d = {'limits': {'B': {'max': cv2.getTrackbarPos('max B', 'Camera'), 'min': cv2.getTrackbarPos('min B', 'Camera')},
                        'G': {'max': cv2.getTrackbarPos('max G', 'Camera'), 'min': cv2.getTrackbarPos('min G', 'Camera')},
                        'R': {'max': cv2.getTrackbarPos('max R', 'Camera'), 'min': cv2.getTrackbarPos('min R', 'Camera')}}}

        # Show original image that is being filtered
        cv2.imshow('Original', image)

        # Checks if there is a mouse event
        cv2.setMouseCallback("Original", partial(onMousePreSetTrackbar, colorBGR=image))

        # Save value for the pressed key ----- Image refresh 25 ms
        key = cv2.waitKey(1)

        # By pressing the j key program will save the parameters of the filter
        if key == ord('j'):

            # Gets the old values with the new one and compares
            resultDiferrent = checkValues(d, dataState)

            # if there are different the's a need to save
            if(resultDiferrent == True):

                # Dumps formated information into var 
                d_json = json.dumps(d, indent=2)

                print("Type the name of the file to save")

                # Let the user choose the name of the file
                file_name = input()
                file_name = (str(file_name) + ".json")

                # Opens file to write
                openFile = open(file_name, "w")

                # Write in file
                openFile.write(d_json)

                # Close file
                openFile.close()

                print("File " + str(file_name) + " as been saved")
                print(Fore.GREEN + "Now you can exit the program safely!!" + Fore.RESET)

            # If there is no diffrence the save comand is no 
            else:
                print("The content is not different, so there's no need to save")

        #------------------------------------------
        #   Termination
        #------------------------------------------

        # By pressing the q key will exit the user from the program
        elif key == ord('q'):

            # Gets the old values with the new one and compares
            resultDiferrent = checkValues(d, dataState)

            # If the user doesn't save the file the program will warn the user about it
            if resultDiferrent == True:
                print(Fore.RED + "Just to remind, you are exiting without saving the file that contain the paremeters of the trackbars" + Fore.RESET)
                print("Are you sure you want to exit without saving?")
                print("Type one of the follow words ----> Save / Don't Save / Cancel")

                # Decision of the user
                decisionWord = input()

                # Saving the paremeters
                if(decisionWord == "Save"):
                    # Dumps formated information into var 
                    d_json = json.dumps(d, indent=2)

                    # Shows the user the aspect of the file saved
                    print(d_json)

                    print("Type the name of the file to save")

                    # Let the user choose the name of the file
                    file_name = input()
                    file_name = (str(file_name) + ".json")

                    # Opens file to write
                    openFile = open(file_name, "w")

                    # Write in file
                    openFile.write(d_json)

                    # Close file
                    openFile.close()

                    print("File " + str(file_name) + " as been saved")
                    print("Exiting program")

                    break
                # Exiting without saving
                elif(decisionWord == "Don't Save"):
                    print("File not saved")

                    break
                # Cancel the quit command
                elif(decisionWord == "Cancel"):
                    print("The quit command was cancelled")
                else:
                    print("Command invalid please try again")
            else:
                print("The content is not different, so there's no need to save")
                break
                

if __name__ == '__main__':
    main()