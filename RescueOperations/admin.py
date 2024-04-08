from django.contrib import admin
from .models import DeviceDetails, Element

class DeviceDetailsAdmin(admin.ModelAdmin):
    list_display = ('user', 'Device_name', 'Device_id', 'Device_location','state')


class ElementAdmin(admin.ModelAdmin):
    list_display = ('device', 'date', 'time', 'location', 'child_state', 'temperature', 'humidity', 'oxygen_level', 'pulse')


admin.site.register(DeviceDetails, DeviceDetailsAdmin)
admin.site.register(Element, ElementAdmin)

