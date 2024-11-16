# Load modules
import re
import sys
import json
import time
import socket
import threading
import cv2 as cv
import numpy as np
from urllib.request import urlopen
from flask_socketio import SocketIO, emit
from flask import Flask, Response, render_template

# Flask setup
app = Flask(__name__)

# Initialize SocketIO
socketio = SocketIO(app)

# Send a command and receive a response
cmd_no = 0
off = [0.007,  0.022,  0.091,  0.012, -0.011, -0.05]

# Shared variable to hold the captured image
current_frame = None

def capture():
    """
    Captures an image from the camera and stores it in the global variable.
    This function runs in a separate thread to ensure the image is updated continuously.
    """
    global current_frame
    while True:
        # Capture the image from the car's camera
        img = capture_image()  # Assuming capture_image() is your current capture() method
        current_frame = img  # Store the image in the shared variable
        time.sleep(0.1)  # Sleep for a short time to simulate continuous capture

def capture_image():
    """
    Capture the image using the camera and return it.
    This is the existing capture() function you provided.
    """
    global cmd_no
    cam = urlopen('http://192.168.4.1/capture')
    img = cam.read()
    img = np.asarray(bytearray(img), dtype='uint8')
    img = cv.imdecode(img, cv.IMREAD_UNCHANGED)
    return img


@app.route('/video_feed')
def video_feed():
    """
    A Flask route to stream the current image to the browser.
    """
    def generate():
        global current_frame
        while True:
            if current_frame is not None:
                # Convert the image to JPEG for streaming
                ret, jpeg = cv.imencode('.jpg', current_frame)
                if ret:
                    # Return the image in the appropriate format for Flask streaming
                    yield (b'--frame\r\n'
                           b'Content-Type: image/jpeg\r\n\r\n' + jpeg.tobytes() + b'\r\n\r\n')
            time.sleep(0.1)  # Sleep to reduce CPU usage
    return Response(generate(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/console_log')
def console_log():
    return render_template('console.html')

# Start the Flask app in a separate thread
def start_flask():
    socketio.run(app, host='0.0.0.0', port=5050)

# Start Flask server in a new thread
flask_thread = threading.Thread(target=start_flask)
flask_thread.daemon = True  # Daemonize the thread to allow the main program to exit
flask_thread.start()

# Start the camera capture in a separate thread
capture_thread = threading.Thread(target=capture)
capture_thread.daemon = True  # Daemonize the thread to allow the main program to exit
capture_thread.start()

def cmd(sock, do, what='', where='', at=''):
    """
    Sends a command to the car and waits for a response.
    
    Args:
        sock (socket.socket): The socket used for communication.
        do (str): The command type (e.g., 'move', 'set', 'stop').
        what (str, optional): Specific action for the command (default is '').
        where (str, optional): Direction for movement (default is '').
        at (str or list, optional): Speed or angle (default is '').
    
    Returns:
        res (int): The response from the car after the command is executed.
    """
    global cmd_no
    cmd_no += 1
    msg = {"H": str(cmd_no)}  # Command header
    
    # Construct the message based on the command type
    if do == 'move':
        msg["N"] = 3
        if where == 'forward':
            msg["D1"] = 3
        elif where == 'back':
            msg["D1"] = 4
        elif where == 'left':
            msg["D1"] = 1
        elif where == 'right':
            msg["D1"] = 2
        msg["D2"] = at  # at is speed here
    elif do == 'set':
        msg.update({"N": 4, "D1": at[0], "D2": at[1]})
    elif do == 'stop':
        msg.update({"N": 1, "D1": 0, "D2": 0, "D3": 1})
    elif do == 'rotate':
        msg.update({"N": 5, "D1": 1, "D2": at})  # at is an angle here
    elif do == 'measure':
        if what == 'distance':
            msg.update({"N": 21, "D1": 2})
    elif do == 'check':
        msg["N"] = 23

    msg_json = json.dumps(msg)  # Convert message to JSON format
    print(f"{cmd_no}: {do} {what} {where} {at}: ", end="")

    # Try to send the message to the car
    try:
        sock.send(msg_json.encode())
    except:
        socketio.emit('console', f"{cmd_no}: {do} {what} {where} {at}")
        sys.exit()

    # Wait for the response
    while 1:
        res = sock.recv(1024).decode()
        if '_' in res:
            break
    res = re.search('_(.*)}', res).group(1)  # Extract the response
    if res == 'ok' or res == 'true':
        res = 1
    elif res == 'false':
        res = 0
    elif msg.get("N") == 21:
        res = round(int(res) * 1.3, 1)  # Correct distance with a factor
    else:
        res = int(res)
    socketio.emit('console', f"{cmd_no}: {do} {what} {where} {at}")
    return res

# Connect to car's WiFi
ip = "192.168.4.1"
port = 100
print(f"Connect to {ip}:{port}")
car = socket.socket()

# Try to establish a connection with the car
try:
    car.connect((ip, port))
except:
    print("Error:", sys.exc_info()[0])
    sys.exit()
print("Connected!")

# Read first data from socket
print(f"Receive from {ip}:{port}")
try:
    data = car.recv(1024).decode()  # Receive data from the car
except:
    print("Error:", sys.exc_info()[0])
    sys.exit()
print("Received:", data)

# Evasion of obstacles
speed = 100         # Car speed
ang = [90, 45, 135] # Head rotation angles for sensor
dist = [0, 0, 0]    # Measured distances to obstacles
dist_min = 30       # Minimum distance to obstacle (cm)

# Evasion of obstacles
def evade_obstacle():
    """
    Handles obstacle evasion with smarter behavior to avoid getting stuck in corners or retrying unnecessary actions.
    """
    print("Obstacle detected! Evading...")
    cmd(car, do='stop')  # Stop the car
    
    # Rotate the sensor to left and right to measure distances
    for i in [1, 2]:
        cmd(car, do='rotate', at=ang[i])
        dist[i] = cmd(car, do='measure', what='distance')
    cmd(car, do='rotate', at=90)  # Re-center the sensor

    # Evaluate distances and decide direction
    if dist[1] > dist_min and dist[2] > dist_min:  # Both sides clear
        print("Clear on both sides. Moving forward.")
        cmd(car, do='move', where='forward', at=speed)
    elif dist[1] > dist_min:  # More space to the left
        print("Turning left to avoid obstacle.")
        cmd(car, do='move', where='left', at=speed)
        time.sleep(0.5)

        # Check if left turn was successful and has enough space to continue
        left_check = cmd(car, do='measure', what='distance')
        if left_check > dist_min:
            print("Space cleared after left turn, continuing.")
            cmd(car, do='move', where='forward', at=speed)
        else:
            print("No space after left turn. Moving backward.")
            cmd(car, do='move', where='back', at=speed)
            time.sleep(0.5)
    elif dist[2] > dist_min:  # More space to the right
        print("Turning right to avoid obstacle.")
        cmd(car, do='move', where='right', at=speed)
        time.sleep(0.5)

        # Check if right turn was successful and has enough space to continue
        right_check = cmd(car, do='measure', what='distance')
        if right_check > dist_min:
            print("Space cleared after right turn, continuing.")
            cmd(car, do='move', where='forward', at=speed)
        else:
            print("No space after right turn. Moving backward.")
            cmd(car, do='move', where='back', at=speed)
            time.sleep(0.5)
    else:  # No space on either side, move backward
        print("No clear path. Moving backward.")
        cmd(car, do='move', where='back', at=speed)
        time.sleep(0.5)

    # Final check after evasive action, if stuck for too long, reset or reverse more
    attempt = 0
    while True:
        front_distance = cmd(car, do='measure', what='distance')
        if front_distance > dist_min or attempt > 3:  # Path cleared or too many failed attempts
            break
        print("Still stuck, retrying evasive action...")
        cmd(car, do='move', where='back', at=speed)
        time.sleep(0.5)
        attempt += 1

    cmd(car, do='stop')  # Stop after avoiding obstacle


# Main loop
cmd(car, do='rotate', at=90)  # Ensure sensor starts centered
cmd(car, do='move', where='forward', at=speed)  # Start moving forward

# Main loop for checking obstacles
while True:
    # Check if car was lifted off the ground to interrupt the loop
    if cmd(car, do='check'):
        print("Car was lifted. Stopping...")
        break

    # Check distance to obstacles
    front_distance = cmd(car, do='measure', what='distance')
    if front_distance <= dist_min:
        evade_obstacle()  # Call evade_obstacle if obstacle detected
        cmd(car, do='move', where='forward', at=speed)  # Resume forward movement

# Close socket
cmd(car, do='stop')  # Ensure car stops
car.close()  # Close the connection
