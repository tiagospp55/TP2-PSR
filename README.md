# TP2-PSR# PSR TP2

# Summary

This project was made as a group practical project for the class of robotical systems programing, at Universidade de Aveiro. It consists of two main scripts. 
The first one, called "color_segmented", is used to configure color detection parameters, allowing the user to see their effects, and saving them to a json file. 
The second one, called "ar_paint.py", uses the color detection parameters present in the json file, result of the first script, to draw in a blank (or not), canvas. For this, it calculates the centroid of the desired color present on the image captured by the user's camera. 
Some of the advanced features that were implemented in the second script include:
-Stability check: prevents lines from being drawn if there is too much instability on the centroid.
-Video canvas: Allows the white canvas to be replaced with the video captured by the user's camera.
-Geometric drawing: Allows the user to draw geometric forms in the screen, such as circles and squares.
-Painting zones generation: Generates zones on the canvas for the user to paint on, according to the requested number of zones input by the user. It also marks them with the color that should be used to paint, red, green or blue.
-Painting grading: Grades the accuracy of the users painting, by showing the percentage of the zones painted in the correct color,

# Usage

While running the color segmented, the user is shown 2 windows, the camera and the mask, which is being done in real-time. In the mask window, 6 trackbars are shown, allowing the user to definte the mask parameters. The configuration can be saved, allowing the parameters to be used elsewhere, letting the user to quickly exit of the program. It can prevent an involutary exit and will ask the user if he wants to save the configuration before doing so.
While using the ar_paint, click "R", "G" or "B" to change colors to red, green or blue, respectively. Pressing the "+" and "-" will allow the user to increase or decrease the pencil size. Using the "C" key will will clear the whiteboard, while the "w" key will save the present state of the whiteboard. Pressing "Q" at any given moment will allow you to quit the program at any time, closing it (and giving you the final grade of your painting if the zone mode is in use).

# Zone mode run example:
./ar_paint.py -j file.json -z -> runs zones mode of the ar paiting

