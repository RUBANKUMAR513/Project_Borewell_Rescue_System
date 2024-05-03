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
            last_element = Element.objects.filter(device=selected_device).order_by('-date', '-time').first()
            if last_element:
                last_location = last_element.location
            else:
                # If no last element exists, set last_location to a default value or None
                last_location = "Current Location Not Found!"
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
            'last_location':last_location,
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
    id = request.GET.get('id')
    
    

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
from test import resultData
import math
import requests
# Serial port where the Arduino is connected; the port may change!
port = 'COM6'
send_data=True
# Function to read from the serial port continuously
# print("data--->",data)
# print("accumulated_data---->",accumulated_data)
def read_serial():
    accumulated_data = ""  # Variable to accumulate received data
    while True:
        try:
            if arduino and arduino.in_waiting > 0:
                
                data = arduino.readline().strip().decode('utf-8')  # Read full line, decode from bytes to string
                print("data--->",data)
                accumulated_data += data
                
                print("accumulated_data---->",accumulated_data)
                if accumulated_data.startswith('<') and accumulated_data.endswith('>'):
                    # If a complete message is received, parse and process it
                    device_id, depth, gas, temperature, humidity, latitude, longitude = parse_serial_data(accumulated_data)
                    print("parse_serial_data---->")
                    print(device_id, depth, gas, temperature, humidity, latitude, longitude)
                    address=get_address(latitude, longitude)
                    print(address)
                    child_state=resultData()
                    print(child_state)

                    try:
                        device = DeviceDetails.objects.get(Device_id=device_id)
                    except DeviceDetails.DoesNotExist:
                        print(f"Device with ID {device_id} does not exist.")
                        continue

                    #  # Create new Element instance
                    element = Element.objects.create(
                        device=device,
                        date=datetime.date.today(),
                        time=datetime.datetime.now().time(),
                        location=address,
                        depth=depth,
                        oxygen_level=gas,
                        temperature=temperature,
                        humidity=humidity,
                        child_state=child_state,
                        pulse=0,
                        latitude=latitude,
                        longitude=longitude,
                     )

                     # Save the Element instance
                    element.save()
                    accumulated_data = ""  # Reset accumulated data

        except serial.SerialException as e:
            print("Serial Exception:", e)
        except PermissionError as e:
            print("Permission Error:", e)




                # Perform further processing with the parsed data
                
        
                # if depth is not None and gas is not None:
                #     if temperature is None:
                #         temperature = 0
                #     if humidity is None:
                #         humidity = 0
                    
                #     device_id = 1  # Assuming device id is 1

                #     # Check if the device exists
                #     try:
                #         device = DeviceDetails.objects.get(Device_id=device_id)
                #     except DeviceDetails.DoesNotExist:
                #         print(f"Device with ID {device_id} does not exist.")
                #         continue

                #     # Create new Element instance
                #     element = Element.objects.create(
                #         device=device,
                #         date=datetime.date.today(),
                #         time=datetime.datetime.now().time(),
                #         location="YourLocation",
                #         depth=depth,
                #         oxygen_level=gas,
                #         temperature=temperature,
                #         humidity=humidity,
                #         child_state='sad',
                #         pulse=0
                #     )

                #     # Save the Element instance
                #     element.save()
                        
def get_address(latitude, longitude):
    
    if latitude == 0.00 and longitude == 0.00:
        return "Current Location Not Found!"

    
    url = f"https://nominatim.openstreetmap.org/reverse?format=json&lat={latitude}&lon={longitude}"

    
    response = requests.get(url)

    
    if response.status_code == 200:
        data = response.json()
        address = data.get('display_name', 'Address not found')
        return address
    else:
        return 'Failed to retrieve address'
        
           

def parse_serial_data(serial_data):
    try:
        if not serial_data.startswith('<') or not serial_data.endswith('>'):
            print("Invalid data format:", serial_data)
            return None, None, None, None, None, None, None
        
        data_str = serial_data[1:-1]  
        data_parts = data_str.split('&')  
        
        values = {}
        for part in data_parts:
            key, value = part.split('=')
            values[key] = value
        print(values)
       
        device_id = values.get('dev', None)
        depth = float(values.get('dep', 0.0))
        gas = float(values.get('gas', 0))
        temperature = float(values.get('tem', 'NAN')) if 'NAN' not in values.get('tem', 'NAN') else 0.0
        humidity = float(values.get('hum', 'NAN')) if 'NAN' not in values.get('hum', 'NAN') else 0.0
        latitude = float(values.get('lat', 0.0))
        longitude = float(values.get('lon', 0.0))

        return device_id, depth, gas, temperature, humidity, latitude, longitude
    except Exception as e:
        print("Error parsing serial data:", e)
        return None, None, None, None, None, None, None





arduino = None
connected_ports = [port.device for port in serial.tools.list_ports.comports()]
if port in connected_ports:
    arduino = serial.Serial(port=port, baudrate=9600, timeout=0.01)
    serial_thread = threading.Thread(target=read_serial)
    serial_thread.daemon = True  
    serial_thread.start()
else:
    print(f"Error: Port {port} is not connected.")


def set_angles(angles):
    if arduino and send_data:  
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


from django.http import StreamingHttpResponse

def generate():
  
    mp_drawing = mp.solutions.drawing_utils
    mp_hands = mp.solutions.hands

 
    joint_list = [[4, 3, 2], [7, 6, 5], [11, 10, 9], [15, 14, 13], [19, 18, 17]]

   
    cap = cv2.VideoCapture(0)

    with mp_hands.Hands(min_detection_confidence=0.8, min_tracking_confidence=0.5, max_num_hands=1) as hands:
        while True:
            ret, frame = cap.read()
            if not ret:
                break

            image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            image = cv2.flip(image, 1)

            
            image.flags.writeable = False
            results = hands.process(image)
            image.flags.writeable = True

            
            if results.multi_hand_landmarks:
                for hand_landmarks in results.multi_hand_landmarks:
                    mp_drawing.draw_landmarks(image, hand_landmarks, mp_hands.HAND_CONNECTIONS)

                
                image, angles = compute_finger_angles(image, results, joint_list)
                set_angles(angles)

         
            image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
            _, jpeg = cv2.imencode('.jpg', image)
            frame = jpeg.tobytes()

            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')


response = StreamingHttpResponse(generate(), content_type='multipart/x-mixed-replace; boundary=frame')


def webcam_feed(request):
    global arduino 

    
    if arduino is None:
        return HttpResponse("Error: Arduino is not connected.")
   
    return StreamingHttpResponse(generate(), content_type='multipart/x-mixed-replace; boundary=frame')



from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json

@csrf_exempt
def update_url(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            url = data.get('url')
           
            print("Received URL:", url)
           
            return JsonResponse({'message': 'URL updated successfully'}, status=200)
        except Exception as e:
            
            return JsonResponse({'error': str(e)}, status=400)
    else:
        
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    

# FACIAL EMOTION DETECTION


from test import facialemotion
from django.http import StreamingHttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt

# Global variable to control streaming
streaming_enabled = True

def test_emotion_view(request):
    return render(request, 'testemotion.html')

@csrf_exempt
def toggle_view(request):
    global streaming_enabled
    
    if request.method == 'POST' and request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        is_on = request.POST.get('is_on')
        
        if is_on == 'true':
            global streaming_enabled
            streaming_enabled = True
            # Start streaming frames
            print("Streaming started")
            return JsonResponse({'message': 'Streaming started'})
        else:
            streaming_enabled = False
            print("Streaming stopped")
            return JsonResponse({'message': 'Streaming stopped'})
    else:
        return JsonResponse({'error': 'Invalid request'})

def stream_frames_view(request):
    print("Inside stream_frames_view") 
    if streaming_enabled:
        print("Streaming is enabled")  
        return StreamingHttpResponse(facialemotion(), content_type="multipart/x-mixed-replace;boundary=frame")
    else:
        print("Streaming is not enabled")
        return JsonResponse({'error': 'Streaming not enabled'})




    