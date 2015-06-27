from django.contrib import admin
from .models import AccessPoint, EthernetNetworkInterface

admin.site.register(AccessPoint)
admin.site.register(EthernetNetworkInterface)
