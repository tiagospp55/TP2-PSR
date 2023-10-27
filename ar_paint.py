#!/usr/bin/env python3
import cv2
import json
import argparse
import numpy as np
from time import ctime
from colorama import Fore
from functools import partial 

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
    cv2.imshow("ola",green_mask)
    mask_image = cv2.add(green_mask, image)
    
    return mask_image, green_mask

def get_connected_components(image):
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        _, binary_image = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY+cv2.THRESH_OTSU)
        cv2.imshow("aa", binary_image)
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
    parser.add_argument('-usp', '--use_shake_pevention', type = int, required=False,help = "Use Shake prevetion for more perfect lines, write the value of the trheshold" )
    parser.add_argument('-um', '--use_mouse', default = False,help = "Use the mouse instead of the red point")
    parser.add_argument('-cam', '--use_camera', help = "Draw directy in the image gived by the camera")
    
    args = vars(parser.parse_args())

    centroids = None

    x = 0
    y = 0
	
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
    
    
    cv2.namedWindow('Canvas')
    cv2.namedWindow('Camera', cv2.WINDOW_AUTOSIZE)

    _, image = capture.read()  # get an image from the camera
    height, width, channels = image.shape
    
	#Create the white canvas with the same size of the camera window
    image_canvas = np.ones((height,width,3), dtype=np.uint8) * 255
    
	#Read data from the json file 
    file_name = args['json']
    openFile = open(file_name)
    data = json.load(openFile)
    print(data)
    openFile.close()


    shake_detection = 1600

    while True:

        ret, image = capture.read()

		#if the read function returns a fail value, the program stops
        if not ret:
            print('No image from camera')
            break

        
		# Read everytime the data present in the .json file
        openFile = open(file_name)
        data = json.load(openFile)
        openFile.close()        
        
		#Process the image and aplly a mask on the chosen area
        mask_image, mask = process_image(image, data, height, width, mask_color)
        
		# Get connected components
        if args['use_mouse']:
            cv2.setMouseCallback("Canvas", partial(mouseCallback, image_canvas=image_canvas, drawing_data=drawing_data))
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
                centroids = None
                drawing_data['pencil_down'] = False
            
            print(drawing_data['pencil_down'])
            if drawing_data['pencil_down']:        
                if drawing_data['last_point'] is not None and centroids is not None:
                    distance = (drawing_data['last_point'] [0]- centroids[0])**2 + (drawing_data['last_point'] [1] - centroids[1])**2

                    if args['use_shake_pevention']:
                        if distance > args['use_shake_pevention']:
                            cv2.circle(image_canvas, centroids, drawing_data['size'], drawing_data['color'], -1)

                if args['use_camera']:
                    cv2.line(mask_image, drawing_data['last_point'] , centroids, drawing_data['color'] , drawing_data['size'] , -1)
                    #Não estou a conseguir fazer
                    
                else:    
                    cv2.line(image_canvas, drawing_data['last_point'] , centroids, drawing_data['color'] , drawing_data['size'] , -1)
                drawing_data['last_point']= centroids
            
        

        cv2.imshow("Work",mask_image)
        cv2.imshow('Canvas', image_canvas)
        
        key = cv2.waitKey(25)

        


        if key == ord('j'):

            d = {'limits': {
                'B': {'max': cv2.getTrackbarPos('max B/H', 'Camera'), 'min': cv2.getTrackbarPos('min B/H', 'Camera')},
                'G': {'max': cv2.getTrackbarPos('max G/S', 'Camera'), 'min': cv2.getTrackbarPos('min G/S', 'Camera')},
                'R': {'max': cv2.getTrackbarPos('max R/V', 'Camera'), 'min': cv2.getTrackbarPos('min R/V', 'Camera')}}}

            

            d_json = json.dumps(d)


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
            image_canvas = np.ones((height,width,3), dtype=np.uint8) * 255

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
            
    capture.release()
    cv2.destroyAllWindows()
if __name__ == '__main__':
    main()