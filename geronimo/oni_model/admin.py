from django.contrib import admin
from .models import AccessPoint,EthernetNetworkInterface,WifiNetworkInterface

admin.site.register(AccessPoint)
admin.site.register(EthernetNetworkInterface)
admin.site.register(WifiNetworkInterface)
