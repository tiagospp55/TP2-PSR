#!/usr/bin/env python3

#Import required modules
from math import sqrt
import math
import cv2
import argparse
import json
import numpy as np
from copy import deepcopy
import colorama
from colorama import Fore, Style, Back
import time
from random import randint


def main():
        # --------------------
        # Initialization
        # --------------------

        #Initialize colorama
        colorama.init(autoreset=True)

        def onMouseClick(event, coordinate_x, coordinate_y, _, __):
                # List of events 0=Move
                # 1=LeftButtonDown 2=RightButtonDown 3=MiddleButtonDown
                # 4=LeftButtonUp 5=RightButtonUp 6=MiddleButtonUp
                if event == 1:
                        # Save coordinates in list
                        centroids_list.append({'cx': coordinate_x, 'cy': coordinate_y})

        #Argparse for input of the JSON file
        parser = argparse.ArgumentParser(description='Augmented reality paint')
        parser.add_argument('-j','--JSON', required = True, 
                        help='Full path to JSON file')
        parser.add_argument('-skd','--use_shake_detection', required = False,
                        default = False, action = 'store_true',
                        help='Activates shake detection while drawing')
        parser.add_argument('-z','--zones', action='store_true', required = False, 
                        help='Display a blank canvas with numbered zones')
        parser.add_argument('-c','--capture', action='store_true', required = False, 
                        help='Display video capture as background')

        args = parser.parse_args()
        json_path = open(args.JSON) # Opens JSON file
        json_file = json.load(json_path) # Reads json file
        create_zones = args.zones # Checks if the program should draw numbered zones
        create_zones_number = 6 # Set the minimum number of zones to create
        use_capture = args.capture # Checks if the program should use video capture as background
        
        print(Style.BRIGHT + Back.LIGHTBLUE_EX + Fore.BLACK+ '[AR_Paint] Press c to clear the drawing.' 
        '\nr, g, b change the pencil color to red, green and blue, respectively.'
        '\n+ increases pencil size, - decreases it'
        '\nw saves the drawing.'
        '\nTo draw shapes, press s for a square, o for a circle and e for an ellipse')
        
        global centroids_list
        color = (0, 0, 0)
        pencil_size = 1
        # Drawing shapes
        start_x = 0; end_x = 0
        start_y = 0; end_y = 0
        start_canvas = None
        drawing_shape = None # Should hold a string with "square" or "circle"
        
        centroids_list = []

        cap = cv2.VideoCapture(0)

        #If capture fails, exit
        if not cap.isOpened():                 
                print("[AR_Paint] Cannot open camera") 
                exit()
        ret, frame = cap.read()
        h, w, c = frame.shape

        #Creates a white image (whiteboard)
        white_board = np.ones((h, w, c),dtype=np.uint8) # 3 channel ones
        white_board = white_board*255 # 3 channel white image
        window_name = 'Visualizing' # Window name


        # Creates the numbered zones if enabled by argument and saves in white_board variable
        if create_zones:
                # Variables for drawing the zones
                number_of_zones = 0
                line_width = 10
                line_color = (0, 0, 0)
                contours = None
                zones = {}

                # Creating a default vertex list
                vertices = []
                vertices.append((0, 0))
                vertices.append((0, int(h/2)))
                vertices.append((0, h))
                vertices.append((int(w/2), 0))
                vertices.append((w, 0))
                vertices.append((w, int(h/2)))
                vertices.append((int(w/2), h))
                vertices.append((w, h))

                # Making the frame
                cv2.line(white_board, vertices[0], vertices[2], line_color, line_width)
                cv2.line(white_board, vertices[0], vertices[4], line_color, line_width)
                cv2.line(white_board, vertices[7], vertices[2], line_color, line_width)
                cv2.line(white_board, vertices[7], vertices[4], line_color, line_width)

                # Create the zones
                while number_of_zones < create_zones_number:
                        v_1 = randint(0,len(vertices)-1)
                        v_2 = randint(0,len(vertices)-1)
                        cv2.line(white_board, vertices[v_1], vertices[v_2], line_color, line_width)

                        gray_image = cv2.cvtColor(white_board, cv2.COLOR_RGB2GRAY)
                        _, black_image = cv2.threshold(gray_image, 128, 255, cv2.THRESH_BINARY)
                        contours,_ = cv2.findContours(black_image, cv2.RETR_CCOMP, cv2.CHAIN_APPROX_TC89_L1)
                        number_of_zones = len(contours)

                # Write the numbers
                for i in range(number_of_zones):
                        moments = cv2.moments(contours[i])
                        try:
                                center = (int(moments['m10']/moments['m00']), int(moments['m01']/moments['m00']))
                        except:
                                continue
                        color_number = randint(1,3)
                        letter_number = ['B','G','R']
                        cv2.putText(white_board, letter_number[color_number-1], center, cv2.FONT_HERSHEY_SIMPLEX, 1, (0,0,0), 2, cv2.LINE_AA)
                        # Save the contours and their color to the zones dictionary
                        zones[i] = {'color': color_number, 'contour': contours[i]}

                # Deleting the variables used to create the numbered zones
                del(number_of_zones)
                del(line_width)
                del(line_color)
                del(contours)
                del(vertices)
                del(gray_image)
                del(black_image)


        blank_board = deepcopy(white_board) # Blank image (used to clear drawing)

        cv2.namedWindow(window_name, cv2.WINDOW_AUTOSIZE)
        cv2.setMouseCallback(window_name, onMouseClick)
       
        pressing = False
        #----------------------
        # Execution
        #----------------------
        while True:
     
                ret, frame = cap.read()
                frame = cv2.flip(frame, 1)
                frame_rgb = deepcopy(frame) #Get a frame 
                if not ret: #If getting fails
                        print("[AR_Paint] Can't receive frame (stream end?). Exiting ...")
                        break

                # Gets frame from webcam and binarizes with thresholds from given limits.json file
                image_b,image_g,image_r = cv2.split(frame_rgb)
                _, image_thresholded_b = cv2.threshold(image_b, json_file['limits']['B']['min'],json_file['limits']['B']['max'], cv2.THRESH_BINARY)
                _, image_thresholded_g = cv2.threshold(image_g, json_file['limits']['G']['min'],json_file['limits']['G']['max'], cv2.THRESH_BINARY)
                _, image_thresholded_r = cv2.threshold(image_r, json_file['limits']['R']['min'],json_file['limits']['R']['max'], cv2.THRESH_BINARY)
                frame_rgb = cv2.merge((image_thresholded_b, image_thresholded_g, image_thresholded_r))
                
                # Converts image to gray 
                gray_image = cv2.cvtColor(frame_rgb, cv2.COLOR_RGB2GRAY)
                output = deepcopy(frame_rgb)
                # Finds shapes in the frame
                contours, _ = cv2.findContours(gray_image, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)

                # If a shape is found then we can process
                if len(contours) != 0:
                        
                        # Find the biggest area of the contour
                        c = max(contours, key = cv2.contourArea)

                        # The biggest contour is drawn here
                        cv2.drawContours(output, c, -1, (255,25), 2)

                        # Bounding Rectangle shape
                        x,y,w,h = cv2.boundingRect(c)

                        #Center of the rectangle
                        cx = int(x + w/2)
                        cy = int(y + h/2)

                        #Draws a red crosshair to show the centroid
                        cv2.line(output, (cx-4, cy), (cx+4, cy), (0, 0, 255), 1)
                        cv2.line(output, (cx, cy-4), (cx, cy+4), (0, 0, 255), 1)

                        # Draws a red crosshair to show the centroid in the original capture
                        cv2.line(frame, (cx-4, cy), (cx+4, cy), (0, 0, 255), 1)
                        cv2.line(frame, (cx, cy-4), (cx, cy+4), (0, 0, 255), 1)

                        # Save coordinates in list
                        centroids_list.append({'cx': cx, 'cy': cy})

                # Line drawing
                if pressing == False:
                        if len(centroids_list) > 2: # Only draws if there's at least 2 points
                                
                                # Get values from list
                                x1 = centroids_list[-2]['cx']
                                y1 = centroids_list[-2]['cy']
                                x2 = centroids_list[-1]['cx']
                                y2 = centroids_list[-1]['cy']
                                # Draws line between two points
                                if args.use_shake_detection == True and abs(x1-x2) > 10:
                                        pass
                                elif args.use_shake_detection == True and abs(y1-y2) > 10:
                                        pass
                                else:
                                        cv2.line(white_board, (x1, y1), (x2, y2), color, pencil_size)


                # Checking if zones are painted correctly
                if create_zones:
                        all_pixels = 0
                        correct_pixels = 0
                        for i in range(len(zones)):
                                mask = np.zeros(frame.shape, dtype=np.uint8) # 3 channel zeros
                                # TODO This command can result in "KeyError: 1"
                                zone_contour = zones[i]['contour']
                                zone_color = zones[i]['color'] - 1
                                cv2.drawContours(mask, [zone_contour], -1, (255,255,255), thickness=cv2.FILLED) # This can result in "KeyError: 1"
                                masked = cv2.bitwise_and(white_board, white_board, mask=mask[:,:,0])
                                # Get the number of correct/all pixels
                                all_pixels += int(np.sum(mask[:,:,0]) / 255)
                                # Deleting the other channels
                                if zone_color == 0:
                                        #delete 2 and 3
                                        #white_pixels = np.sum(np.add(masked[:,:,1]/255, masked[:,:,2]/255)/2)
                                        #white_pixels = all_pixels - cv2.countNonZero(masked)
                                        #white_pixels = np.sum(masked[:,:,0])/255
                                        white_pixels = int(np.sum(cv2.bitwise_and(masked[:,:,1], masked[:,:,2], mask=None)/255))
                                elif zone_color == 1:
                                        #delete 1 and 3
                                        #white_pixels = np.sum(np.add(masked[:,:,0]/255, masked[:,:,2]/255)/2)
                                        #white_pixels = all_pixels - cv2.countNonZero(masked)
                                        #white_pixels = np.sum(masked[:,:,1])/255
                                        white_pixels = int(np.sum(cv2.bitwise_and(masked[:,:,0], masked[:,:,2], mask=None)/255))
                                elif zone_color == 2:
                                        #delete 1 and 2
                                        #white_pixels = np.sum(np.add(masked[:,:,0]/255, masked[:,:,1]/255)/1)
                                        #white_pixels = all_pixels - cv2.countNonZero(masked)
                                        #white_pixels = np.sum(masked[:,:,2])/255
                                        white_pixels = int(np.sum(cv2.bitwise_and(masked[:,:,0], masked[:,:,1], mask=None)/255))
                                correct_pixels += int(np.sum(masked[:,:,zone_color]) / 255) - white_pixels
                        zone_percentage = (correct_pixels/all_pixels)*100
                        print(f"[AR_Paint] {zone_percentage:.6f}% complete!", end="\r")

                        

                #----------------------
                # Visualization
                #----------------------
                if use_capture:
                        blended_board = cv2.addWeighted (white_board, 0.5, frame, 0.5, 0)
                        concat_1 = cv2.hconcat([blended_board, output]) # Joins white board and output in the same window
                else:       
                        concat_1 = cv2.hconcat([white_board, output]) # Joins white board and output in the same window
                concat_2 = cv2.hconcat([concat_1, frame]) # Joins the previous join with the camera capture
                cv2.imshow(window_name, concat_2) #Shows the concatenate
                
                #----------------------
                # Termination
                #----------------------
        
                pressed_key = cv2.waitKey(1) 

                if pressed_key == ord('q'): # Quit command
                        print(Fore.RED + '[AR_Paint] Quitting program')
                        break

                elif pressed_key == ord('c'): # Clear the drawing
                        print(Fore.RED + '[AR_Paint] You cleared the drawing')
                        centroids_list = []
                        white_board = deepcopy(blank_board)

                elif pressed_key == ord('r'): # Change color to red
                        print(Fore.RED + '[AR_Paint] You changed color to red')
                        color = (0, 0, 255)

                elif pressed_key == ord('g'): # Change color to green
                        print(Fore.GREEN + '[AR_Paint] You changed color to green')
                        color = (0, 255, 0)

                elif pressed_key == ord('b'): # Change color to blue
                        print(Fore.BLUE + '[AR_Paint] You changed color to blue')
                        color = (255, 0, 0)

                elif pressed_key == ord('+'): # Increase line size
                        print(Style.BRIGHT + '[AR_Paint] You increased pencil size')
                        pencil_size += 1

                elif pressed_key == ord('-'): # Decrease line size
                        print(Style.DIM + '[AR_Paint] You decreased pencil size')
                        if pencil_size > 1:
                                pencil_size -= 1

                elif pressed_key == ord('w'): # Save the image
                        date = time.strftime("%Y%m%d_%H%M%S", time.localtime())
                        filename = 'drawing_' + str(date) + '.png'
                        cv2.imwrite(filename, white_board)
                        print(Style.DIM + '[AR_Paint] Your artwork has been saved in {} ;)'.format(filename))
               
                elif pressed_key == ord('s') and pressing == False: # Starts drawing the rectangle
                        pressing = not pressing
                        drawing_shape = "square"
                        start_x = centroids_list[-1]['cx']
                        start_y = centroids_list[-1]['cy']
                        start_canvas = deepcopy(white_board)
                        print('[AR_Paint] Started the rectangle')

                elif pressed_key == ord('s') and pressing == True: # Finishes drawing the rectangle
                        pressing = not pressing
                        drawing_shape = None
                        end_x = centroids_list[-1]['cx']
                        end_y = centroids_list[-1]['cy']
                        white_board = deepcopy(start_canvas)
                        cv2.rectangle(white_board, (start_x, start_y), (end_x, end_y), color, pencil_size)
                        print('[AR_Paint] Finished the rectangle')
                              
                elif pressing == True and drawing_shape == "square": # Shows the rectangle while it's being drawn
                        end_x = centroids_list[-1]['cx']
                        end_y = centroids_list[-1]['cy']
                        white_board = deepcopy(start_canvas)
                        cv2.rectangle(white_board, (start_x, start_y), (end_x, end_y), color, pencil_size)
                
                elif pressed_key == ord('o') and pressing == False: # Starts drawing the circle
                        pressing = not pressing
                        drawing_shape = 'circle'
                        start_x = centroids_list[-1]['cx']
                        start_y = centroids_list[-1]['cy']
                        start_canvas = deepcopy(white_board)
                        print('[AR_Paint] Started the circle')

                elif pressed_key == ord('o') and pressing == True: # Finishes drawing the circle
                        pressing = not pressing
                        drawing_shape = None
                        end_x = centroids_list[-1]['cx']
                        end_y = centroids_list[-1]['cy']                        
                        radius = int(sqrt((end_x-start_y)**2 + (end_y-start_y)**2))
                        white_board = deepcopy(start_canvas)
                        cv2.circle(white_board, (start_x, start_y), radius, color, pencil_size)
                        print('[AR_Paint] Finished the circle')

                elif pressing == True and drawing_shape == "circle": # Shows the circle while it's being drawn
                        end_x = centroids_list[-1]['cx']
                        end_y = centroids_list[-1]['cy']
                        radius = int(sqrt((end_x-start_y)**2 + (end_y-start_y)**2))
                        white_board = deepcopy(start_canvas)
                        cv2.circle(white_board, (start_x, start_y), radius, color, pencil_size)    

                elif pressed_key == ord('e') and pressing == False: # Starts drawing the ellipse
                        pressing = not pressing
                        drawing_shape = 'ellipse'
                        start_x = centroids_list[-1]['cx']
                        start_y = centroids_list[-1]['cy']
                        start_canvas = deepcopy(white_board)
                        print('[AR_Paint] Started the ellipse')

                elif pressed_key == ord('e') and pressing == True: # Finishes drawing the ellipse
                        pressing = not pressing
                        drawing_shape = None
                        end_x = centroids_list[-1]['cx']
                        end_y = centroids_list[-1]['cy']
                        d = abs(int((end_x - start_x)/2))
                        D = abs(int((end_y - start_y)/2))
                        degrees = math.degrees(math.atan2(end_y-start_y, end_x-start_x))
                        radius = int(sqrt((end_x-start_y)**2 + (end_y-start_y)**2))
                        white_board = deepcopy(start_canvas)
                        cv2.ellipse(white_board,(start_x, start_y),(d,D), degrees, 0, 360, color, pencil_size)
                        print('[AR_Paint] Finished the ellipse')

                elif pressing == True and drawing_shape == "ellipse": # Shows the ellipse while it's being drawn
                        end_x = centroids_list[-1]['cx']
                        end_y = centroids_list[-1]['cy']
                        d = abs(int((end_x - start_x)/2))
                        D = abs(int((end_y - start_y)/2))
                        degrees = math.degrees(math.atan2(end_y-start_y, end_x-start_x))
                        radius = int(sqrt((end_x-start_y)**2 + (end_y-start_y)**2))
                        white_board = deepcopy(start_canvas)
                        cv2.ellipse(white_board,(start_x, start_y),(d,D), degrees, 0, 360, color, pencil_size)

if __name__ == '__main__':
    main()