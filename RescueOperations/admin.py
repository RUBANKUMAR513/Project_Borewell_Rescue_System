from django.contrib import admin
from .models import DeviceDetails, Element ,Notification

class DeviceDetailsAdmin(admin.ModelAdmin):
    list_display = ('user', 'Device_name', 'Device_id', 'Device_location','state')


class ElementAdmin(admin.ModelAdmin):
    list_display = ('device', 'date', 'time', 'location', 'child_state', 'temperature', 'humidity', 'oxygen_level', 'pulse')


class NotificationAdmin(admin.ModelAdmin):
    list_display = ('user', 'message', 'date', 'time', 'read', 'deviceId_or_global')
    search_fields = ['user__username']




admin.site.register(DeviceDetails, DeviceDetailsAdmin)
admin.site.register(Element, ElementAdmin)
admin.site.register(Notification,NotificationAdmin)

