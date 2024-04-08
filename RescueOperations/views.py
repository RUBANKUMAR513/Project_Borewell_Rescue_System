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
from django.contrib.auth import authenticate, login as auth_login
from django.http import HttpResponse
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import inch

 

def index(request):
    return render(request,'Login.html')


@login_required
def Dashboard(request):
    if request.session.get('user_type') == 'regular':
        user_id = request.session.get('user_id')
        devices = DeviceDetails.objects.filter(user_id=user_id)
        username = request.session.get('username').capitalize()
        context = {'username': username, 'devices': devices}
        return render(request, 'index-3.html', context)
    else:
        return redirect('/login')
 
    

from .models import DeviceDetails, Element

from django.shortcuts import get_object_or_404

@login_required
def deviceDashboard(request):
    if request.user.is_authenticated:
        devices = DeviceDetails.objects.filter(user=request.user)
        selected_device_id = request.GET.get('device_id')
        selected_device = None
        elements = None

        if selected_device_id:
            selected_device = get_object_or_404(DeviceDetails, id=selected_device_id, user=request.user)
            elements = Element.objects.filter(device=selected_device)

        context = {
            'user_id': request.user.id,
            'username': request.user.username.capitalize(),
            'devices': devices,
            'elements': elements,
            'selected_device': selected_device,
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
        # Add more styles if needed
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
