import datetime

from django.shortcuts import render, get_object_or_404

from oni_model.models import AccessPoint, RoutingLink, EthernetNetworkInterface, InterfaceRoutingLink
from oni_model.serializer import AccessPointSerializer, RoutingLinkSerializer, \
        InterfaceRoutingLinkSerializer, EthernetNetworkInterfaceSerializer

from rest_framework import mixins
from rest_framework import filters
from rest_framework import generics
from rest_framework.views import APIView
from rest_framework.response import Response


# willkuerliche Festlegungen (deutlich laenger als die jeweils typische Aktualisierungsperiode)
EXPIRE_AGE_MINUTES = {"link": 120,
                      "interface": 48 * 60,
                      "accesspoint": 30 * 60,
                     }


# bei Listen-Darstellugen filtern wir nach Alter
def filter_by_timestamp_age(queryset, max_age_minutes):
    min_timestamp = datetime.datetime.now() - datetime.timedelta(minutes=max_age_minutes)
    return queryset.filter(timestamp__gte=min_timestamp)


## abstract classes
class ListView(mixins.ListModelMixin,
               mixins.CreateModelMixin,
               generics.GenericAPIView):

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)

    # make this an uninstanceable class
    class Meta:
        abstract = True


class DetailView(mixins.RetrieveModelMixin,
                 mixins.UpdateModelMixin,
                 generics.GenericAPIView):

    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    # make this an uninstanceable class
    class Meta:
        abstract = True


class AccessPointList(ListView):
    """Liefert eine Liste aller WLAN Accesspoints des Opennets"""

    serializer_class = AccessPointSerializer

    def get_queryset(self):
        return filter_by_timestamp_age(AccessPoint.objects.all(), EXPIRE_AGE_MINUTES["accesspoint"])


class AccessPointDetail(DetailView):
    """Liefert die Details eines WLAN Accesspoints des Opennets"""

    queryset = AccessPoint.objects.all()
    serializer_class = AccessPointSerializer


class AccessPointLinksList(ListView):
    """Liefert eine Liste aller Links zwischen Accesspoints des Opennets"""

    serializer_class = RoutingLinkSerializer

    def get_queryset(self):
        return filter_by_timestamp_age(RoutingLink.objects.all(), EXPIRE_AGE_MINUTES["link"])


class AccessPointLinksDetail(ListView):
    """Alle Links zu diesem WLAN Accesspoints des Opennets"""

    serializer_class = RoutingLinkSerializer

    def get_queryset(self):
        ip = self.kwargs["ip"]
        ap = get_object_or_404(AccessPoint, main_ip=ip)
        return filter_by_timestamp_age(ap.get_links(), EXPIRE_AGE_MINUTES["link"], "timestamp")


class AccessPointInterfacesList(ListView):
    """Liefert eine Liste aller Interfaces von Accesspoints des Opennets"""

    serializer_class = EthernetNetworkInterfaceSerializer
    queryset = EthernetNetworkInterface.objects.all()


class NetworkInterfaceDetail(DetailView):
    """Ein Interface mit einer spezifischen IP"""

    lookup_field = "ip_address"
    queryset = EthernetNetworkInterface.objects.all()
    serializer_class = EthernetNetworkInterfaceSerializer


class NetworkInterfaceAccessPoint(DetailView):
    """Der AP der zu einer IP gehoert"""

    serializer_class = AccessPointSerializer

    def retrieve(self, request, ip_address=None):
        interface = get_object_or_404(EthernetNetworkInterface, ip_address=ip_address)
        return Response(self.serializer_class(interface.access_point).data)


class AccessPointInterfacesDetail(ListView):
    """Alle Interfaces eines Accesspoints des Opennets"""

    serializer_class = EthernetNetworkInterfaceSerializer

    def retrieve(self, request, ip_address=None):
        ap = get_object_or_404(AccessPoint, main_ip=ip_address)
        return Response(self.serializer_class(ap.interfaces).data)
