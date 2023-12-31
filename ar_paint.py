#!/usr/bin/env python3
from pprint import pprint
from random import randint
import cv2
import json
import argparse
import numpy as np
from time import ctime
from colorama import Back, Fore, Style
from functools import partial 
from math import sqrt
# process the image given by the camera to create the mask 
def process_image(image, data, height, width, mask_color):
    bmin = data['limits']['B']['min']
    bmax = data['limits']['B']['max']
    gmin = data['limits']['G']['min']
    gmax = data['limits']['G']['max']
    rmin = data['limits']['R']['min']
    rmax = data['limits']['R']['max']

    mask = cv2.inRange(image,(bmin,gmin,rmin), (bmax,gmax,rmax)) 
       

    green_mask = np.zeros((height,width ,3), np.uint8)
    green_mask[mask > 0] = mask_color
  
    mask_image = cv2.add(green_mask, image)
    
    return mask_image, green_mask

def get_connected_components(image):
        """Get connected components of binary image."""

           # Convert to grayscale
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        # Threshold to binary image
        _, binary_image = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY+cv2.THRESH_OTSU)
        # Find connected components
        num_labels, labels, stats, centroids = cv2.connectedComponentsWithStats(binary_image, connectivity=4)
        return num_labels, labels, stats, centroids
        # Use connectedComponentsWithStats to label connected components
		


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



def main():
    parser = argparse.ArgumentParser(description='Definition of ' + Fore.BLUE + 'test ' + Fore.RESET + 'mode')
    parser.add_argument('-j', '--json', type=str, required=True, help='Full path to' + Fore.YELLOW + ' json ' + Fore.RESET + 'file.')
    parser.add_argument('-mc', '--mask_color', type=str, choices = ['green','red','blue'], required=False, help = 'Choose the color of the mask. Ex: Type ' + Fore.RED + ' red ' + Fore.RESET + 'to represent: [' + Fore.RED + '255' + Fore.RESET + ',' +Fore.GREEN + '0' + Fore.RESET + ',' + Fore.BLUE + '0' + Fore.RESET + ']' )
    parser.add_argument('-usp', '--use_shake_pevention', required=False, action = 'store_true',help = "Use Shake prevetion for more perfect lines, write the value of the trheshold" )
    parser.add_argument('-um', '--use_mouse', default = False,action = 'store_true',help = "Use the mouse instead of the red point")
    parser.add_argument('-cam', '--use_camera',action = 'store_true', help = "Draw directy in the image gived by the camera")
    parser.add_argument('-z','--zones', action='store_true', required = False, help='Display a blank canvas with numbered zones')
    
    args = vars(parser.parse_args())

    print('Welcome to the drawing game!') 
    print('To change your drawing color to blue, red or green, press ' + Back.BLUE + '"B"' + Style.RESET_ALL + ', ' + Back.RED + '"R"' + Style.RESET_ALL + 
          ' or ' + Back.GREEN + '"G"' + Style.RESET_ALL + ', respectively.')
    print('If you want to change your pencil size, press ' + Fore.BLACK + Back.LIGHTYELLOW_EX +  '"+"' + Style.RESET_ALL + ' or '+ Fore.BLACK  + Back.LIGHTYELLOW_EX +  '"-"' + Style.RESET_ALL + ' to increase and decrease it\'s size, respectively!')
    print('Hate what you\'re drawing? Press '+ Fore.BLACK  + Back.LIGHTGREEN_EX +  '"C"' + Style.RESET_ALL + 
          ' to clear the board! Want to boast about your drawing skills instead? Press '+ Fore.BLACK + Back.LIGHTGREEN_EX +'"w"' + Style.RESET_ALL + ' to save the drawing board')
    print('When you\'re done creating the masterpiece of a lifetime, press ' + Back.LIGHTRED_EX + '"Q"' + Style.RESET_ALL + ' to quit the game.')
    


	
    if args['use_mouse']:
        cv2.namedWindow('Canva Draw')
        drawing_data = {'pencil_down': False, 'previous_x': 0, 'previous_y': 0, 'color': (0,0,0), 'size': 1}
    else:
        drawing_data = {'pencil_down': False, 'last_point': None, 'color': (0,0,0), 'size': 5}

    # initial setup
    capture = cv2.VideoCapture(0)

    if args['mask_color']:
        if(args['mask_color'] == 'green'):
            mask_color = (0,255,0)
        elif(args['mask_color'] == 'red'):
            mask_color = (0,0,255)
        else:
            mask_color = (255,0,0) 
    else:
        mask_color = (0,255,0)
    
    
    cv2.namedWindow('Canva Draw')
   

    _, image = capture.read()  # get an image from the camera
    height, width, channels = image.shape
    
	 # Creates the numbered zones if enabled by argument and saves in white_board variable
    if args['zones']:

        image_canvas = np.ones((height,width,3), dtype=np.uint8) * 255
        image_zones = np.ones((height,width,3), dtype=np.uint8) * 255

        # Variables for drawing the zones
        number_of_zones = 0
        line_width = 10
        line_color = (0, 0, 0)
        contours = None
        zones = {}

        print("How many zones do you want to paint?")
        create_zones_number = input()

        # Creating a default vertex list
        vertices = []
        vertices.append((0, 0))
        vertices.append((0, int(height/2)))
        vertices.append((0, height))
        vertices.append((int(width/2), 0))
        vertices.append((width, 0))
        vertices.append((width, int(height/2)))
        vertices.append((int(width/2), height))
        vertices.append((width, height))

        # Making the frame
        cv2.line(image_canvas, vertices[0], vertices[2], line_color, line_width)
        cv2.line(image_canvas, vertices[0], vertices[4], line_color, line_width)
        cv2.line(image_canvas, vertices[7], vertices[2], line_color, line_width)
        cv2.line(image_canvas, vertices[7], vertices[4], line_color, line_width)
        cv2.line(image_zones, vertices[0], vertices[2], line_color, line_width)
        cv2.line(image_zones, vertices[0], vertices[4], line_color, line_width)
        cv2.line(image_zones, vertices[7], vertices[2], line_color, line_width)
        cv2.line(image_zones, vertices[7], vertices[4], line_color, line_width)

        # Create the zones
        while number_of_zones < int(create_zones_number):
            v_1 = randint(0,len(vertices)-1)
            v_2 = randint(0,len(vertices)-1)
            cv2.line(image_canvas, vertices[v_1], vertices[v_2], line_color, line_width)
            cv2.line(image_zones, vertices[v_1], vertices[v_2], line_color, line_width)

            gray_image = cv2.cvtColor(image_canvas, cv2.COLOR_RGB2GRAY)
            _, black_image = cv2.threshold(gray_image, 128, 255, cv2.THRESH_BINARY)
            contours,_ = cv2.findContours(black_image, cv2.RETR_CCOMP, cv2.CHAIN_APPROX_TC89_L1)
            number_of_zones = len(contours)

        # Write the zone label
        for i in range(number_of_zones):
            moments = cv2.moments(contours[i])
            try:
                center = (int(moments['m10']/moments['m00']), int(moments['m01']/moments['m00']))
            except:
                continue

            color_number = randint(1,3)
            letter_number = ['B','G','R']
            cv2.putText(image_canvas, letter_number[color_number-1], center, cv2.FONT_HERSHEY_SIMPLEX, 1, (0,0,0), 2, cv2.LINE_AA)
            cv2.putText(image_zones, letter_number[color_number-1], center, cv2.FONT_HERSHEY_SIMPLEX, 1, (0,0,0), 2, cv2.LINE_AA)
            # Save the contours and their color to the zones dictionary
            zones[i] = {'color': color_number, 'contour': contours[i]}

    else:
        #Create the white canvas with the same size of the camera window
        image_canvas = np.ones((height,width,3), dtype=np.uint8) * 255
        image_zones = np.ones((height,width,3), dtype=np.uint8) * 255

	#Read data from the json file 
    file_name = args['json']
    openFile = open(file_name)
    data = json.load(openFile)
    print(data)
    openFile.close()

    shake_detection = 1600
    flag_first = True
    while True:

        ret, image_base = capture.read()

		#if the read function returns a fail value, the program stops
        if not ret:
            print('No image from camera')
            break

        image = cv2.flip(image_base,1)

		# Read everytime the data present in the .json file
        openFile = open(file_name)
        data = json.load(openFile)
        openFile.close()        
        
		#Process the image and aplly a mask on the chosen area
        mask_image, mask = process_image(image, data, height, width, mask_color)
        
		# Get connected components
        if args['use_mouse']:
            cv2.setMouseCallback("Canva Draw", partial(mouseCallback, image_canvas=image_canvas, drawing_data=drawing_data))
        else:
            num_labels, labels, stats, centroids = get_connected_components(mask)
            if num_labels > 1:
                max_label, _ = max([(i, stats[i, cv2.CC_STAT_AREA]) for i in range(1, num_labels)], key=lambda x: x[1])
                centroids = (int(centroids[max_label][0]), int(centroids[max_label][1]))
                m = np.equal(labels, max_label)
                b,g,r = cv2.split(mask_image)
                b[m] = 0
                r[m] = 0
                g[m] = 0
                mask_image = cv2.merge((b,g,r))
                cv2.line(mask_image, (centroids[0]+5, centroids[1]), (centroids[0]-5, centroids[1]), (0,0,255), 5, -1)
                cv2.line(mask_image, (centroids[0], centroids[1]+5), (centroids[0], centroids[1]-5), (0,0,255), 5, -1)
                drawing_data['pencil_down'] = True
            else:
                print("No color")
                drawing_data['pencil_down'] = False
            
            if drawing_data['pencil_down']:        
                if drawing_data['last_point'] is not None and centroids is not None:
                    distance = (drawing_data['last_point'] [0]- centroids[0])**2 + (drawing_data['last_point'] [1] - centroids[1])**2

                    if args['use_shake_pevention']:
                        if distance > shake_detection:
                            cv2.circle(image_canvas, centroids, 1, drawing_data['color'], -1)
                x,y = centroids
                x += 1
                y +=1
                if flag_first == True:
                    cv2.line(image_canvas, (x,y) , centroids, drawing_data['color'] , drawing_data['size'] , -1)
                else:
                    cv2.line(image_canvas, drawing_data['last_point'] , centroids, drawing_data['color'] , drawing_data['size'] , -1)

                drawing_data['last_point']= centroids

            if args["use_camera"]:
                maskCamera = np.not_equal(cv2.cvtColor(image_canvas, cv2.COLOR_BGR2GRAY), 255)
                maskCamera = np.repeat(maskCamera[:,:,np.newaxis], 3, axis=2)
                output = image.copy()
                
                output[maskCamera] = image_canvas[maskCamera]

            else:
                output = image_canvas
                    #Não estou a conseguir fazer
         # Checking if zones are painted correctly
        if args['zones']:
            all_pixels = 0
            correct_pixels = 0
            for i in range(len(zones)):
                    mask = np.zeros(image.shape, dtype=np.uint8) # 3 channel zeros
                    # TODO This command can result in "KeyError: 1"
                    zone_contour = zones[i]['contour']
                    zone_color = zones[i]['color'] - 1
                    cv2.drawContours(mask, [zone_contour], -1, (255,255,255), thickness=cv2.FILLED)
                    masked = cv2.bitwise_and(image_canvas, image_canvas, mask=mask[:,:,0])
                    # Get the number of correct/all pixels
                    all_pixels += int(np.sum(mask[:,:,0]) / 255)
                    # Deleting the other channels
                    if zone_color == 0:
                            white_pixels = int(np.sum(cv2.bitwise_and(masked[:,:,1], masked[:,:,2], mask=None)/255))
                    elif zone_color == 1:
                            white_pixels = int(np.sum(cv2.bitwise_and(masked[:,:,0], masked[:,:,2], mask=None)/255))
                    elif zone_color == 2:
                            white_pixels = int(np.sum(cv2.bitwise_and(masked[:,:,0], masked[:,:,1], mask=None)/255))
                    correct_pixels += int(np.sum(masked[:,:,zone_color]) / 255) - white_pixels
            zone_percentage = (correct_pixels/all_pixels)*100
            print(f'{zone_percentage:.2f}% complete!')
        
        if args["use_camera"]:
            cv2.imshow('Camera Draw', output)
        else:
            cv2.imshow("Canva Draw", image_canvas)


        if not args['use_mouse']:
            cv2.imshow("Camera",mask_image)
        
        flag_first = False
        key = cv2.waitKey(25)
        
        if key == ord('j'):

            d = {'limits': {
                'B': {'max': cv2.getTrackbarPos('max B', 'Camera'), 'min': cv2.getTrackbarPos('min B', 'Camera')},
                'G': {'max': cv2.getTrackbarPos('max G', 'Camera'), 'min': cv2.getTrackbarPos('min G', 'Camera')},
                'R': {'max': cv2.getTrackbarPos('max R', 'Camera'), 'min': cv2.getTrackbarPos('min R', 'Camera')}}}

            d_json = json.dumps(d)

            file_name = args['json']

            openFile = open(file_name, "w")

            openFile.write(d_json)

            openFile.close()
        
        elif key == ord('q'):
            if zone_percentage < 50.0: # Low grade result
                print(Back.RED+Fore.WHITE+'You have quit the game. The drawing was '+str(round(zone_percentage,2)) +'% complete. You could have at least tried...'+Style.RESET_ALL)
            elif zone_percentage < 80.0 and zone_percentage >= 50.0: # Acceptable grade result
                print(Back.YELLOW+Fore.WHITE+'You have quit the game. The drawing was '+str(round(zone_percentage,2)) +'% complete. Nice try!'+Style.RESET_ALL)
            elif zone_percentage >= 80.0: # High grade result
                print(Back.BLUE+Fore.WHITE+'You have quit the game. The drawing was '+str(round(zone_percentage,2)) +'% complete. Good job!!'+Style.RESET_ALL)
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
            elif drawing_data['size'] >= 5:
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
            #image_canvas = np.ones((height,width,3), dtype=np.uint8) * 255

            temp = cv2.flip(image_zones, 0)
            image_canvas = cv2.flip(temp, 0)
           
            # TODO how to clear canvas?

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
        elif key == ord('o'):
            print("Circle")
            xNew = None
            yNew = None
            if flagCircle == True:    
                flagCircle = False
                if len(centroids) != 1:
                    x_initial,y_initial = centroids
            else:
                if len(centroids) != 1:
                    xNew, yNew = centroids
            if xNew is not None and yNew is not None:
                radius = int(sqrt((x_initial - xNew)**2+(x_initial - xNew)**2))
                cv2.circle(image_canvas, (x_initial, y_initial), radius, drawing_data['color'], -1)
        

        elif key == ord('s'):
            print("Square")
            xNew = None
            yNew = None
            if flagSquare == True:    
                flagSquare = False
                if len(centroids) != 1:
                    x_initial,y_initial = centroids
            else:
                if len(centroids) != 1:
                    xNew, yNew = centroids

                if xNew is not None and yNew is not None:
                    cv2.rectangle(image_canvas, (x_initial , y_initial),(xNew, yNew), drawing_data['color'], -1)
        elif key != ord('s') and key != ord('o'):
            flagSquare = True 
            flagCircle = True

    capture.release()
    cv2.destroyAllWindows()
if __name__ == '__main__':
    main()