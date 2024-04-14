import mediapipe as mp
import cv2 
import numpy as np 
import serial
import threading


# Serial port where the Arduino is connected; the port may change!
port = 'COM6'

# Create a serial object 
arduino = serial.Serial(port=port, baudrate=9600, timeout=0.01)

# Flag to control whether to send data or not
send_data = True


#
#   This function continuously reads from the serial port and prints received data
#
def read_serial():
    while True:
        if arduino.in_waiting > 0:
            data = arduino.readline().strip()
            print("Receiving: ", data)


# Start the thread to continuously read from the serial port
serial_thread = threading.Thread(target=read_serial)
serial_thread.daemon = True  # Daemonize the thread so it will be terminated when the main program exits
serial_thread.start()


#
#   This function takes a list containing the angles of all the fingers 
#   and sends it to the Arduino via serial 
#
def set_angles(angles):
    if send_data:  # Check if the flag to send data is set
        msg = ''
        for angle in angles:
            a = str(angle)
            while len(a) < 3:
                a = '0' + a
            msg += a
        msg = '<' + msg + '>'
        print("Sending: ", msg)    
        for c in msg:
            arduino.write(bytes(c, 'utf-8'))


#
#   This function computes the angles of each finger and renders them onto the image
#
def compute_finger_angles(image, results, joint_list):

    angles = []

    for hand in results.multi_hand_landmarks:
        for i, joint in enumerate(joint_list):
            a = np.array([hand.landmark[joint[0]].x, hand.landmark[joint[0]].y])
            b = np.array([hand.landmark[joint[1]].x, hand.landmark[joint[1]].y])
            c = np.array([hand.landmark[joint[2]].x, hand.landmark[joint[2]].y])

            rad = np.arctan2(c[1] - b[1], c[0] - b[0]) - np.arctan2(a[1] - b[1], a[0] - b[0])
            angle = np.abs(rad*180.0/np.pi)

            if angle > 180:
                angle = 360 - angle
            
            if i == 0:
                angle = np.interp(angle,[90,180],[0, 200])
                angle = min(180, angle)
            else:
                angle = np.interp(angle,[30,180],[0, 180])
                angle = min(180, angle)

            angles.append(int(angle))
            cv2.putText(image, str(round(angle, 2)), tuple(np.multiply(b, [640, 480]).astype(int)), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (30, 30, 30), 2, cv2.LINE_AA)
    return image, angles


# Setup mediapipe
mp_drawing = mp.solutions.drawing_utils
mp_hands = mp.solutions.hands

# Define which landmarks should be considered for the fingers angles 
joint_list = [ [4, 3, 2], [7, 6, 5], [11, 10, 9], [15, 14, 13], [19, 18, 17]]

while True:  # Run an infinite loop
    if send_data:
        # Setup webcam feed
        cap = cv2.VideoCapture(0)
    
    with mp_hands.Hands(min_detection_confidence=0.8, min_tracking_confidence=0.5, max_num_hands=1) as hands:
        while send_data:  # Check if the flag to send data is set
            # Capture webcam image and convert it from BGR to RGB
            ret, frame = cap.read()
            image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
            # Flip the image horizontally
            image = cv2.flip(image, 1)
            
            # Detect the hand with MediaPipe
            image.flags.writeable = False
            results = hands.process(image)
            image.flags.writeable = True
    
            # Render detections
            if results.multi_hand_landmarks:
                for num, hand in enumerate(results.multi_hand_landmarks):
                    
                    # Render the detected landmarks 
                    mp_drawing.draw_landmarks(image, hand, mp_hands.HAND_CONNECTIONS, 
                                                mp_drawing.DrawingSpec(color=(0, 0, 155), thickness=2, circle_radius=4),
                                                mp_drawing.DrawingSpec(color=(0, 0, 255), thickness=2, circle_radius=2))
    
                # Compute the angles and send them to the Arduino
                image, angles = compute_finger_angles(image, results, joint_list)
                set_angles(angles)
            
            # Convert the image back to RGB
            image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
            cv2.imshow('Hand Tracking', image)
    
            # End the loop if <q> is pressed
            if cv2.waitKey(10) & 0xFF == ord('q'):
                send_data = False  # Stop sending data
                break
    
    # Release webcam feed
    if send_data:
        cap.release()
        cv2.destroyAllWindows() 