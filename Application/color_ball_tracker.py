"""
Color Ball Tracker,
Created by: Michael Bozall,
Date: 2021-08-25,
Modified by: Rodrigo Barba,
Date: 2024-11-14,
Description: This script captures an image from a camera, filters it for a specified color, detects contours, and calculates the distance and angle to a detected object. It then sends commands to a robot to locate and track the object while avoiding obstacles.
"""




# Load modules
import re                        # Regular expressions
import sys                       # System-specific parameters and functions
import json                      # JSON parsing and manipulation
import time                      # Time-related functions
import socket                    # Networking support
import imutils                   # Additional OpenCV utilities
import cv2 as cv                 # OpenCV for computer vision tasks
import numpy as np               # Numerical operations with arrays
from urllib.request import urlopen  # To fetch images from a URL




# Define color ranges for filtering
color_ranges = {
    "green": (np.array([50, 70, 60], dtype="uint8"), np.array([90, 255, 255], dtype="uint8")),
    "blue": (np.array([100, 150, 0], dtype="uint8"), np.array([140, 255, 255], dtype="uint8")),
    "red": (np.array([0, 150, 100], dtype="uint8"), np.array([10, 255, 255], dtype="uint8")),
    "red2": (np.array([170, 150, 100], dtype="uint8"), np.array([180, 255, 255], dtype="uint8"))
}

# Capture image from camera
cv.namedWindow('Camera')         # Create a named window for displaying the camera feed
cv.moveWindow('Camera', 0, 0)    # Position the window at the top-left corner of the screen

cmd_no = 0  # Initialize the command number counter

# Function to switch between colors
def switch_color(color="green") -> tuple:
    """
    Switches to the desired color HSV range for detection.
    Accepts "green", "blue", or "red" as input.
    """
    if color == "green":
        return color_ranges["green"]
    elif color == "blue":
        return color_ranges["blue"]
    elif color == "red":
        return color_ranges["red"]
    elif color == "red2":  # for the second red range due to HSV wraparound
        return color_ranges["red2"]
    else:
        print("Invalid color. Defaulting to green.")
        return color_ranges["green"]

def capture():
    """
    Captures an image from a camera, filters it for a specified color,
    detects contours, and calculates the distance and angle to a detected object.
    
    Returns:
        ball (int): Indicates if a ball is detected (1 if detected, 0 otherwise).
        dist (float): Calculated distance to the ball.
        ang_rad (float): Angle to the ball in radians.
        ang_deg (int): Angle to the ball in degrees.
    """
    global cmd_no
    cmd_no += 1
    print(str(cmd_no) + ': capture image', end=': ')

    # Switch color filter before processing
    lu_color_vision = switch_color('red2')  # Switch to the desired color (e.g., 'green', 'blue', or 'red')
    
    # Fetch image from the camera
    cam = urlopen('http://192.168.4.1/capture')  # Open the camera URL
    img = cam.read()                             # Read the image bytes
    img = np.asarray(bytearray(img), dtype='uint8')  # Convert bytes to a NumPy array
    img = cv.imdecode(img, cv.IMREAD_UNCHANGED)  # Decode the image
    
    # Filter image by color
    mask = cv.medianBlur(img, 5)                  # Apply median blur to reduce noise
    img_hsv = cv.cvtColor(mask, cv.COLOR_BGR2HSV) # Convert the image to HSV color space
    mask = cv.inRange(img_hsv, lu_color_vision[0], lu_color_vision[1])  # Apply color filter
    
    # Detect contours
    mask = cv.erode(mask, None, iterations=2)     # Erode to reduce noise
    mask = cv.dilate(mask, None, iterations=2)    # Dilate to restore object size
    cont = cv.findContours(mask.copy(), cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)  # Find contours
    cont = imutils.grab_contours(cont)            # Grab the contour list
    
    # Initialize variables for contour evaluation
    yh = 491          # Y-coordinate of the horizon line
    ball = 0          # Flag indicating the presence of a ball
    dist = None       # Distance to the ball
    ang_rad = 0       # Angle to the ball in radians
    ang_deg = 0       # Angle to the ball in degrees
    area = 0          # Contour area
    area_max = 20     # Minimum contour area to consider
    ncont = len(cont) # Number of contours detected
    
    # Evaluate contours
    if ncont > 0:
        for n in range(ncont):
            M = cv.moments(cont[n])  # Calculate moments of the contour
            _xc = int(M['m10'] / M['m00'])  # X-coordinate of the contour center
            _yc = 600 - int(M['m01'] / M['m00'])  # Adjust Y-coordinate to start at image bottom
            area = M['m00']             # Contour area
            
            # Select the largest valid contour below the horizon
            if _yc < yh and area > area_max:
                area_max = area
                ball = 1  # Mark a ball as detected
                nc = n    # Index of the selected contour
                xc = _xc - 400  # Center x-coordinate relative to the image center
                yc = _yc
                center = (_xc, 600 - _yc)  # Center point for visualization
    
    # Calculate distance and angle to the ball
    if ball:
        cv.drawContours(img, cont, nc, (0, 0, 255), 1)  # Highlight the selected contour in red
        cv.circle(img, center, 1, (0, 0, 255), 2)       # Mark the center of the ball
        cv.putText(img, '(' + str(xc) + ', ' + str(yc) + ')', center,
                   cv.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1, cv.LINE_AA)  # Annotate coordinates
        dy = 4.31 * (745.2 + yc) / (yh - yc)  # Calculate distance along the y-axis
        if xc < 0: dy = dy * (1 - xc / 1848)  # Apply correction for negative x-coordinates
        dx = 0.00252 * xc * dy                # Calculate distance along the x-axis
        dist = np.sqrt(dx**2 + dy**2)         # Calculate the total distance
        ang_rad = np.arctan(dx / dy)          # Calculate the angle in radians
        ang_deg = round(ang_rad * 180 / np.pi)  # Convert the angle to degrees
        print('bd =', round(dist), 'ba =', ang_deg)  # Print distance and angle
    else:
        print('no ball')  # No valid ball detected
    
    # Draw guidelines
    cv.line(img, (400, 0), (400, 600), (0, 0, 255), 1)  # Vertical center line
    cv.line(img, (0, 600 - yh), (800, 600 - yh), (0, 0, 255), 1)  # Horizon line
    
    # Display the image
    cv.imshow('Camera', img)
    cv.waitKey(1)  # Wait briefly to refresh the display
    
    return ball, dist, ang_rad, ang_deg  # Return detection results




# Send a command and receive a response
off = [0.007, 0.022, 0.091, 0.012, -0.011, -0.05]  # Offsets for sensor calibration

def cmd(sock, do, what='', where='', at=''):
    """
    Sends a command to the robot and processes the response.

    Parameters:
        sock (socket.socket): The socket connection to the robot.
        do (str): The action to perform (e.g., 'move', 'set', 'stop').
        what (str): Additional information about the action (e.g., 'distance', 'motion').
        where (str): Direction for movement (e.g., 'forward', 'back', 'left', 'right').
        at (varied): Additional data such as speed, angle, or sensor reading configuration.

    Returns:
        res (int/float/list): The processed response from the robot.
    """
    global cmd_no
    cmd_no += 1  # Increment the command counter
    msg = {"H": str(cmd_no)}  # Initialize the command message as a dictionary with a header

    # Determine the type of command and construct the message accordingly
    if do == 'move':
        msg["N"] = 3  # Command type for movement
        what = ' car '
        if where == 'forward':
            msg["D1"] = 3  # Direction forward
        elif where == 'back':
            msg["D1"] = 4  # Direction backward
        elif where == 'left':
            msg["D1"] = 1  # Direction left
        elif where == 'right':
            msg["D1"] = 2  # Direction right
        msg["D2"] = at  # 'at' represents speed here
        where = where + ' '  # Add a space for logging

    elif do == 'set':
        msg.update({"N": 4, "D1": at[0], "D2": at[1]})  # Set speed using a tuple (at)
        what = ' speed '

    elif do == 'stop':
        msg.update({"N": 1, "D1": 0, "D2": 0, "D3": 1})  # Stop the robot
        what = ' car'

    elif do == 'rotate':
        msg.update({"N": 5, "D1": 1, "D2": at})  # Rotate the robot's head to an angle (at)
        what = ' head'
        where = ' '

    elif do == 'measure':
        if what == 'distance':
            msg.update({"N": 21, "D1": 2})  # Measure distance
        elif what == 'motion':
            msg["N"] = 6  # Measure motion
        what = ' ' + what

    elif do == 'check':
        msg["N"] = 23  # Check if the robot is off the ground
        what = ' off the ground'

    # Convert the message dictionary to JSON format
    msg_json = json.dumps(msg)
    print(str(cmd_no) + ': ' + do + what + where + str(at), end=': ')

    # Send the message and handle potential errors
    try:
        sock.send(msg_json.encode())  # Send the JSON message over the socket
    except:
        print('Error: ', sys.exc_info()[0])  # Log the error
        sys.exit()  # Exit the program if an error occurs

    # Wait for a valid response
    while True:
        res = sock.recv(1024).decode()  # Receive the response
        if '_' in res:  # Check if the response contains the delimiter
            break

    # Extract the relevant portion of the response
    res = re.search('_(.*)}', res).group(1)

    # Process the response based on the command type
    if res == 'ok' or res == 'true':
        res = 1  # Successful response
    elif res == 'false':
        res = 0  # Negative response
    elif msg.get("N") == 5:
        time.sleep(0.5)  # Allow time for the head to rotate
    elif msg.get("N") == 21:
        res = round(int(res) * 1.3, 1)  # Correct the distance measurement
    elif msg.get("N") == 6:
        res = res.split(",")  # Split the motion data into components
        res = [int(x) / 16384 for x in res]  # Convert to units of g
        res[2] = res[2] - 1  # Subtract 1G from the z-axis measurement
        res = [round(res[i] - off[i], 4) for i in range(6)]  # Apply calibration offsets
    else:
        res = int(res)  # Convert the response to an integer for other cases

    # Log the response
    print(res)

    return res  # Return the processed response




# Define the IP address and port of the car's WiFi
ip = "192.168.4.1"  # IP address of the car
port = 100          # Port number for communication
print('Connect to {0}:{1}'.format(ip, port))  # Log connection attempt

# Create a socket object for the connection
car = socket.socket()

# Try to connect to the car's WiFi
try:
    car.connect((ip, port))  # Connect to the specified IP and port
except:
    # Handle any connection errors
    print('Error: ', sys.exc_info()[0])  # Print the error message
    sys.exit()  # Exit the program if connection fails

print('Connected!')  # Confirm successful connection

#%% Read first data from socket
print('Receive from {0}:{1}'.format(ip, port))  # Log data reception attempt

# Try to receive initial data from the socket
try:
    data = car.recv(1024).decode()  # Receive up to 1024 bytes and decode the message
except:
    # Handle any errors during data reception
    print('Error: ', sys.exc_info()[0])  # Print the error message
    sys.exit()  # Exit the program if data reception fails

print('Received: ', data)  # Log the received data




# Define movement and measurement parameters
speed = 100  # Car speed
ang_tol = 10  # Tolerance for rotation angle (degrees)
ang = [90, ang_tol, 180 - ang_tol]  # Head rotation angles (center, left, right)
dist = [0, 0, 0]  # Measured distances to obstacles at the defined angles
dist_min = 30  # Minimum safe distance to an obstacle (cm)
d180 = 90  # Equivalent rotation distance for a 180-degree turn
dturn = 60  # Equivalent rotation distance for smaller turns

def find_ball():
    """
    Locates the ball by rotating the robot's head and measuring distances.
    
    Steps:
    1. Rotate the head to predefined angles and measure distances.
    2. Detect the presence of a ball in the camera feed.
    3. If the ball is detected and within an acceptable distance, adjust the robot's position to face it.
    """
    time.sleep(0.5)  # Pause briefly before starting the search
    found = 0  # Flag to indicate if the ball was found

    # Perform two search cycles
    for n in range(2):
        # In the second cycle, turn the robot based on distance measurements
        if n == 1:
            if dist[1] > dist[2]:  # Check distances to decide the turn direction
                cmd(car, do='move', where='right', at=speed)  # Move right
            else:
                cmd(car, do='move', where='left', at=speed)  # Move left
            time.sleep(d180 / speed)  # Wait for the 180-degree turn to complete
            cmd(car, do='stop')  # Stop the robot

        # Rotate the head to each predefined angle and measure distances
        for i in range(3):
            cmd(car, do='rotate', at=ang[i])  # Rotate head to the current angle
            dist[i] = cmd(car, do='measure', what='distance')  # Measure distance
            ball, bd, ba_rad, ba_deg = capture()  # Capture image and detect ball
            
            # If a ball is detected, refine measurements
            if ball:
                if ((i == 1 and ba_deg < -ang_tol) or 
                    (i == 2 and ba_deg > +ang_tol)):
                    # Adjust head angle to align more precisely with the ball
                    um_ang = ang[i] - ba_deg
                    cmd(car, do='rotate', at=um_ang)  # Rotate to the updated angle
                    d = cmd(car, do='measure', what='distance')  # Measure distance
                    ball, bd, ba_rad, ba_deg = capture()  # Re-capture and re-detect
                else:
                    um_ang = ang[i]  # Use the current angle
                    d = dist[i]  # Use the measured distance
                
                # If no ball is detected after adjustment, skip
                if not ball:
                    continue
                
                # If the detected ball is beyond the minimum safe distance
                if d > dist_min:
                    found = 1  # Mark ball as found
                    print('found ball: bdist =', round(bd, 1), 'dist =', d)

                    # Rotate head back to the center
                    cmd(car, do='rotate', at=90)
                    
                    # Calculate the steering angle to face the ball
                    steer_ang = 90 - um_ang + ba_deg
                    if steer_ang > ang_tol:  # If the angle is to the right
                        cmd(car, do='move', where='right', at=speed)  # Move right
                    elif steer_ang < -ang_tol:  # If the angle is to the left
                        cmd(car, do='move', where='left', at=speed)  # Move left
                    
                    # Log the steering angle and adjust position
                    print('steering angle =', steer_ang)
                    time.sleep(dturn / speed * abs(steer_ang) / 180)  # Adjust position
                    cmd(car, do='stop')  # Stop the robot
                    time.sleep(0.5)  # Pause briefly
                    _, bd, ba_rad, ba_deg = capture()  # Re-capture the image
                
                break  # Exit the current angle loop once the ball is found
        
        # Exit the main search loop if the ball is found
        if found:
            break

    # If the ball is not found, reset head position
    if not found:
        cmd(car, do='rotate', at=90)  # Rotate head back to the center




#%% Function to track the ball
def track_ball():
    """
    Tracks the ball by calculating the turning radius and adjusting wheel speeds.
    """
    # Capture the current image and check for the ball
    ball, bd, ba_rad, ba_deg = capture()
    if ball:
        # Calculate the turning radius needed to approach the ball
        r = bd / (2 * np.sin(ba_rad))  # Required turning radius
        if r > 0 and r <= 707:  # If the radius indicates a right turn
            s0 = 1.111          # Speed ratio for turning right
            ra = -17.7          # Radius offset for right turns
            rb = 98.4           # Radius factor for right turns
        else:  # For left turns or moving straight
            s0 = 0.9557         # Speed ratio to move straight
            ra = 5.86           # Radius offset for left turns
            rb = -55.9          # Radius factor for left turns

        # Calculate speed ratio for the left and right wheels
        speed_ratio = s0 * (r - ra) / (r + rb)  # Adjust speed based on radius
        speed_ratio = max(0, speed_ratio)  # Ensure speed ratio is non-negative

        # Determine wheel speeds based on the turning direction
        if r > 0 and r <= 707:  # Right turn
            lspeed = speed      # Left wheel speed (full speed)
            rspeed = round(speed * speed_ratio)  # Right wheel speed
        else:  # Left turn or moving straight
            lspeed = round(speed * speed_ratio)  # Left wheel speed
            rspeed = speed      # Right wheel speed

        # Send the speed command to the robot
        cmd(car, do='set', at=[rspeed, lspeed])




#%% Main logic
# Start by centering the robot's head
cmd(car, do='rotate', at=90)

# Find the ball before starting the loop
find_ball()

# Infinite loop to track the ball and handle obstacles
while 1:
    # Check if the robot has been lifted off the ground
    if cmd(car, do='check'):
        break  # Exit the loop if the robot is lifted

    # Track the ball and adjust movement
    track_ball()

    # Measure the distance to obstacles
    if cmd(car, do='measure', what='distance') <= dist_min:
        # If an obstacle is detected, stop the robot
        cmd(car, do='stop')
        # Re-locate the ball after stopping
        find_ball()

#%% Close socket connection
car.close()  # Close the connection to the robot's WiFi
