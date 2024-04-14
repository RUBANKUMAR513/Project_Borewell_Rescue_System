from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login ,logout
from django.contrib.auth.models import User
from django.contrib import messages
from django.urls import reverse
from django.views.decorators.csrf import csrf_protect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import update_session_auth_hash
from datetime import date, time
from datetime import datetime
from django.http import HttpResponse,JsonResponse
from django.core import serializers
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from .models import DeviceDetails
from .models import Notification
from django.contrib.auth import authenticate, login as auth_login
from django.http import HttpResponse
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import inch
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import DeviceDetails, Element
from django.shortcuts import get_object_or_404 

def index(request):
    return render(request,'Login.html')


@login_required
def Dashboard(request):
    if request.session.get('user_type') == 'regular':
        user_id = request.session.get('user_id')
        
        devices = DeviceDetails.objects.filter(user_id=user_id)
        username = request.session.get('username').capitalize()
        global_notifications = Notification.objects.filter(user_id=user_id, deviceId_or_global='global')
        unread_notifications_count = global_notifications.filter(read=False).count()
        context = {'username': username, 'devices': devices, 'global_notifications': global_notifications,'unread_notifications_count': unread_notifications_count}
        return render(request, 'index-3.html', context)
    else:
        return redirect('/login')
    


@login_required
def deviceDashboard(request):
    if request.user.is_authenticated:
        devices = DeviceDetails.objects.filter(user=request.user)
        print(devices)
        selected_device_id = request.GET.get('device_id')
        print('device_id',selected_device_id)
        selected_device = None
        elements = None
        notifications = None

        if selected_device_id:
            selected_device = get_object_or_404(DeviceDetails, id=selected_device_id, user=request.user)
            print(selected_device.state)
            elements = Element.objects.filter(device=selected_device)
            notifications = Notification.objects.filter(user=request.user,deviceId_or_global=selected_device_id)
            unread_notifications_count = notifications.filter(read=False).count()
        context = {
            'user_id': request.user.id,
            'username': request.user.username.capitalize(),
            'devices': devices,
            'elements': elements,
            'selected_device': selected_device,
            'global_notifications': notifications,
            'unread_notifications_count': unread_notifications_count,
        }
        
        return render(request, 'data-table.html', context)
    else:
        return redirect('/login')





@csrf_protect
def login_view(request):
    if request.method == "POST":
        email_or_username = request.POST.get("email_or_username")
        password = request.POST.get("password")
        if not email_or_username or not password:
            messages.error(request, "Please enter both email/username and password.")
            return render(request, 'login-register.html', {'email_or_username': email_or_username})

        user = None
        user = authenticate(email=email_or_username, password=password)
        if user is None:
            
            user = authenticate(username=email_or_username, password=password)

        if user is not None:
            auth_login(request, user)
            request.session['user_id'] = user.id
            request.session['username'] = user.username
            request.session['user_type'] = 'admin' if user.is_superuser else 'regular'
            if user.is_superuser:
                return redirect('admin:index')
            else:
                return redirect('/dashboard')
        else:
            messages.error(request, "Invalid email/username or password.")
            return render(request, 'login-register.html', {'email_or_username': email_or_username})

    return render(request, 'login-register.html')

   
def logout_view(request):
    if 'user_type' in request.session:
        del request.session['user_type']
    if 'user_id' in request.session:
        del request.session['user_id']
    if 'username' in request.session:
        del request.session['username']
    logout(request)
    return redirect('/login')
      

def generate_pdf(request):
    currentDeviceID = request.GET.get('deviceID')
    currentDeviceName=request.GET.get('deviceName')
    id=request.GET.get('id')
    print(currentDeviceID)

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="ChildRescue.pdf"'

    pdf = SimpleDocTemplate(response, pagesize=letter)
    styles = getSampleStyleSheet()
    center_style = ParagraphStyle(name='Center', parent=styles['Normal'], alignment=1)
    content = []

    title = Paragraph("<b>CHILD RESCUE SYSTEM</b><br/><br/>", center_style)
    content.append(title)
    content.append(Spacer(1, 0.2 * inch))

    phone_email = Paragraph("<b>Phone:</b> +0450-387575-5849<br/><b>Email:</b> info@borewellchildrescuesystem.co.in", styles['Normal'])
    content.append(phone_email)
    content.append(Spacer(1, 0.5 * inch))

    table_data = [['DeviceName','DeviceID','Date', 'Time', 'Temperature', 'Humidity', 'Child State', 'Oxygen Level','Pulse']]

    elements = Element.objects.filter(device_id=id)
    print()

    for element in elements:
        table_data.append([
            currentDeviceName,
            currentDeviceID,
            element.date,
            element.time,
            element.temperature,
            element.humidity,
            element.child_state,
            element.oxygen_level,
            element.pulse,
        ])

    table = Table(table_data)
    style = TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        
    ])
    table.setStyle(style)
    content.append(table)

    pdf.build(content)

    return response


import csv
from django.http import HttpResponse
from .models import Element

def generate_csv(request):
    currentDeviceID = request.GET.get('deviceID')
    currentDeviceName = request.GET.get('deviceName')
    id=request.GET.get('id')
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="childRescue.csv"'

    writer = csv.writer(response)
    writer.writerow(['DeviceName', 'DeviceID', 'Date', 'Time', 'Temperature', 'Humidity', 'Child State', 'Oxygen Level', 'Pulse'])

    elements = Element.objects.filter(device_id=id)

    for element in elements:
        writer.writerow([
            currentDeviceName,
            currentDeviceID,
            element.date,
            element.time,
            element.temperature,
            element.humidity,
            element.child_state,
            element.oxygen_level,
            element.pulse,
        ])
    
    return response

@receiver(post_save, sender=Notification)
def delete_old_notifications(sender, instance, **kwargs):
    user_notifications = Notification.objects.filter(user=instance.user)
    if user_notifications.count() > 100:
        notifications_to_delete = user_notifications.order_by('date', 'time')[:user_notifications.count() - 100]
        notifications_to_delete.delete()



# Import necessary libraries
# Import necessary libraries
import cv2
import numpy as np
import mediapipe as mp
import threading
import serial
import serial.tools.list_ports
import datetime
from django.http import StreamingHttpResponse
from django.shortcuts import render
import math
# Serial port where the Arduino is connected; the port may change!
port = 'COM6'
send_data=True
# Function to read from the serial port continuously
def read_serial():
    while True:
        try:
            if arduino and arduino.in_waiting > 0:
                data = arduino.readline().strip()
                print("Receiving: ", data)
                
                # Parse serial data
                depth, gas, temperature, humidity = parse_serial_data(data)

                if depth is not None and gas is not None:
                    if temperature is None:
                        temperature = 0
                    if humidity is None:
                        humidity = 0
                    
                    device_id = 1  # Assuming device id is 1

                    # Check if the device exists
                    try:
                        device = DeviceDetails.objects.get(Device_id=device_id)
                    except DeviceDetails.DoesNotExist:
                        print(f"Device with ID {device_id} does not exist.")
                        continue

                    # Create new Element instance
                    element = Element.objects.create(
                        device=device,
                        date=datetime.date.today(),
                        time=datetime.datetime.now().time(),
                        location="YourLocation",
                        depth=depth,
                        oxygen_level=gas,
                        temperature=temperature,
                        humidity=humidity,
                        child_state='sad',
                        pulse=0
                    )

                    # Save the Element instance
                    element.save()
                        

        except serial.SerialException as e:
            print("Serial Exception:", e)
            # Reconnect to the serial port or handle the exception appropriately
        except PermissionError as e:
            print("Permission Error:", e)
            # Handle the permission error, e.g., by notifying the user or retrying after some time

def parse_serial_data(serial_data):
    # Parse the received data string
    try:
        data_str = serial_data.decode('utf-8')  # Decode bytes to string
        data_str = data_str.strip()[2:-1]  # Remove b'' and trailing newline
        data_parts = data_str.split('&')  # Split by '&'

        # Extract depth, gas, temperature, humidity from data_parts
        depth_str, gas_str, temp_str, hum_str = data_parts
        
        depth = float(depth_str.split('=')[1])  # Extract depth value
        gas = int(gas_str.split('=')[1])  # Extract gas value
        temperature = float(temp_str.split('=')[1]) if 'NAN' not in temp_str else None  # Extract temperature value
        humidity = float(hum_str.split('=')[1]) if 'NAN' not in hum_str else None  # Extract humidity value

        return depth, gas, temperature, humidity
    except Exception as e:
        print("Error parsing serial data:", e)
        return None, None, None, None


# Start the thread to continuously read from the serial port
arduino = None
connected_ports = [port.device for port in serial.tools.list_ports.comports()]
if port in connected_ports:
    arduino = serial.Serial(port=port, baudrate=9600, timeout=0.01)
    serial_thread = threading.Thread(target=read_serial)
    serial_thread.daemon = True  # Daemonize the thread so it will be terminated when the main program exits
    serial_thread.start()
else:
    print(f"Error: Port {port} is not connected.")

# Function to set angles and send them to Arduino
def set_angles(angles):
    if arduino and send_data:  # Check if the flag to send data is set
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

# Function to compute finger angles and render them onto the image
def compute_finger_angles(image, results, joint_list):
    angles = []

    for hand in results.multi_hand_landmarks:
        for i, joint in enumerate(joint_list):
            a = np.array([hand.landmark[joint[0]].x, hand.landmark[joint[0]].y])
            b = np.array([hand.landmark[joint[1]].x, hand.landmark[joint[1]].y])
            c = np.array([hand.landmark[joint[2]].x, hand.landmark[joint[2]].y])

            rad = np.arctan2(c[1] - b[1], c[0] - b[0]) - np.arctan2(a[1] - b[1], a[0] - b[0])
            angle = np.abs(rad * 180.0 / np.pi)

            if angle > 180:
                angle = 360 - angle

            if i == 0:
                angle = np.interp(angle, [90, 180], [0, 200])
                angle = min(180, angle)
            else:
                angle = np.interp(angle, [30, 180], [0, 180])
                angle = min(180, angle)

            angles.append(int(angle))
            cv2.putText(image, str(round(angle, 2)), tuple(np.multiply(b, [640, 480]).astype(int)),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (30, 30, 30), 2, cv2.LINE_AA)
    return image, angles

# Function to generate frames
from django.http import StreamingHttpResponse

def generate():
    # Setup mediapipe
    mp_drawing = mp.solutions.drawing_utils
    mp_hands = mp.solutions.hands

    # Define which landmarks should be considered for the fingers angles
    joint_list = [[4, 3, 2], [7, 6, 5], [11, 10, 9], [15, 14, 13], [19, 18, 17]]

    # Setup webcam feed
    cap = cv2.VideoCapture(0)

    with mp_hands.Hands(min_detection_confidence=0.8, min_tracking_confidence=0.5, max_num_hands=1) as hands:
        while True:
            ret, frame = cap.read()
            if not ret:
                break

            image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            image = cv2.flip(image, 1)

            # Detect hand landmarks
            image.flags.writeable = False
            results = hands.process(image)
            image.flags.writeable = True

            # Render detections
            if results.multi_hand_landmarks:
                for hand_landmarks in results.multi_hand_landmarks:
                    mp_drawing.draw_landmarks(image, hand_landmarks, mp_hands.HAND_CONNECTIONS)

                # Compute angles and send them to Arduino
                image, angles = compute_finger_angles(image, results, joint_list)
                set_angles(angles)

            # Convert image back to BGR
            image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
            _, jpeg = cv2.imencode('.jpg', image)
            frame = jpeg.tobytes()

            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

# Set the response headers to indicate a multipart response
response = StreamingHttpResponse(generate(), content_type='multipart/x-mixed-replace; boundary=frame')


def webcam_feed(request):
    global arduino  # Access the global arduino variable

    # Check if the Arduino is connected
    if arduino is None:
        return HttpResponse("Error: Arduino is not connected.")
    
    # If Arduino is connected, proceed with streaming the webcam feed
    return StreamingHttpResponse(generate(), content_type='multipart/x-mixed-replace; boundary=frame')



