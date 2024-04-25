from django.db import models
from django.contrib.auth.models import User
from django.contrib.auth.models import AbstractUser


class DeviceDetails(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    Device_name = models.CharField(max_length=100)
    Device_id = models.CharField(max_length=100, unique=True)
    Device_location = models.CharField(max_length=100)
    state=models.CharField(max_length=100,default='off')

    def __str__(self):
        return f"Details for {self.user.username}'s {self.Device_name}"



class Element(models.Model):
    device = models.ForeignKey(DeviceDetails, on_delete=models.CASCADE)

    date = models.DateField()
    time = models.TimeField(null=True, blank=True)
    latitude = models.CharField(max_length=20, default='0.0')  # Default latitude value
    longitude = models.CharField(max_length=20, default='0.0')  # Default longitude value
    location = models.CharField(max_length=100)  
    child_state = models.CharField(max_length=20)
    temperature = models.DecimalField(max_digits=5, decimal_places=2)  
    humidity = models.DecimalField(max_digits=5, decimal_places=2)  
    oxygen_level = models.DecimalField(max_digits=5, decimal_places=2)  
    pulse = models.IntegerField()
    depth = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)
    
    
    def __str__(self):
        return f"Element for {self.device.Device_name} on {self.date} at {self.time}"


class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.CharField(max_length=255)
    date = models.DateField()
    time = models.TimeField()
    read = models.BooleanField(default=False)
    deviceId_or_global= models.CharField(max_length=50) 
    
    class Meta:
        ordering = ['-date', '-time']




