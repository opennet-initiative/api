import datetime
import json

from django.shortcuts import get_object_or_404
import djgeojson.serializers
from rest_framework import generics
from rest_framework import mixins
from rest_framework.filters import BaseFilterBackend
from rest_framework.response import Response

from on_geronimo.oni_model.models import (AccessPoint, RoutingLink, EthernetNetworkInterface)
from on_geronimo.oni_model.serializer import (
    AccessPointSerializer, RoutingLinkSerializer, EthernetNetworkInterfaceSerializer)


# nach dreißig Tagen gelten APs nicht mehr als "flapping", sondern als "offline"
# Vorsicht: Werte synchron halten mit der "flapping"-Unterscheidung im der on-map-Kartendarstellung
OFFLINE_AGE_MINUTES = 30 * 24 * 60
FLAPPING_AGE_MINUTES = 30


# abstract classes
class ListView(mixins.ListModelMixin,
               mixins.CreateModelMixin,
               generics.GenericAPIView):

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    # make this an uninstanceable class
    class Meta:
        abstract = True


class DetailView(mixins.RetrieveModelMixin,
                 mixins.UpdateModelMixin,
                 generics.GenericAPIView):

    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    # make this an uninstanceable class
    class Meta:
        abstract = True


def _get_model_fieldnames(model):
    return [field.name for field in model._meta.get_fields()]


def get_geojson_serializer_selector(non_geojson_serializer_class, properties=None):
    def wrapped(self):
        wanted_format = self.request.query_params.get('data_format', None)
        if wanted_format == "geojson":
            class GeoSerializer:
                def __init__(self, queryset, **kwargs):
                    json_string = djgeojson.serializers.Serializer().serialize(
                        queryset, geometry_field="position", properties=properties,
                        with_modelname=False)
                    self.data = json.loads(json_string)
            return GeoSerializer
        else:
            return non_geojson_serializer_class
    return wrapped


class OnlineStatusFilter(BaseFilterBackend):
    """ filter objects by the a timestamp attribute into all/online/flapping/offline categories

    Query arguments:
        * status: online/flapping/offline
    Attributes:
        * last_online_timestamp_field: name of the timestamp field (default: "timestamp")
    """

    def _filter_by_timestamp_age(self, queryset, timedelta_minutes, timestamp_attribute):
        """ bei Listen-Darstellugen filtern wir nach Alter

        Ein positiver "timedelta_minutes"-Wert führt zur Auslieferung von Objekten, deren
        Zeitstempel älter als die angegebene Anzahl von Minuten ist. Ein negativer Wert liefert die
        Objekte aus, deren Zeitstempel jünger ist (vergleichbar mit der "-mtime"-Konvention).
        """
        limit_timestamp = datetime.datetime.now() - datetime.timedelta(
            minutes=abs(timedelta_minutes))
        # different objects use different attribute names for their timestamp
        if timedelta_minutes > 0:
            cmp_func = "lte"
        else:
            cmp_func = "gte"
        args = {"%s__%s" % (timestamp_attribute, cmp_func): limit_timestamp}
        return queryset.filter(**args)

    def filter_queryset(self, request, queryset, view):
        wanted_status = request.query_params.get('status', 'online')
        timestamp_field = getattr(view, "last_online_timestamp_field", "timestamp")
        if wanted_status == "all":
            return queryset
        elif wanted_status == "online":
            return self._filter_by_timestamp_age(
                queryset, -FLAPPING_AGE_MINUTES, timestamp_field)
        elif wanted_status == "offline":
            return self._filter_by_timestamp_age(
                queryset, OFFLINE_AGE_MINUTES, timestamp_field)
        elif wanted_status == "flapping":
            flapping_or_dead = self._filter_by_timestamp_age(
                queryset, FLAPPING_AGE_MINUTES, timestamp_field)
            return self._filter_by_timestamp_age(
                flapping_or_dead, -OFFLINE_AGE_MINUTES, timestamp_field)
        else:
            return []


class AccessPointList(generics.ListAPIView):
    """ Liefert eine Liste aller WLAN Accesspoints des Opennets """

    serializer_class = AccessPointSerializer
    filter_backends = (OnlineStatusFilter, )
    queryset = AccessPoint.objects.all()
    last_online_timestamp_field = "lastseen_timestamp"


class AccessPointDetail(DetailView):
    """Liefert die Details eines WLAN Accesspoints des Opennets"""

    queryset = AccessPoint.objects.all()
    serializer_class = AccessPointSerializer


class AccessPointLinksList(generics.ListAPIView):
    """Liefert eine Liste aller Links zwischen Accesspoints des Opennets"""

    serializer_class = RoutingLinkSerializer
    filter_backends = (OnlineStatusFilter, )
    queryset = RoutingLink.objects.all()


class AccessPointLinksDetail(generics.ListAPIView):
    """Alle Links zu diesem WLAN Accesspoints des Opennets"""

    serializer_class = RoutingLinkSerializer
    filter_backends = (OnlineStatusFilter, )

    def get_queryset(self):
        ip = self.kwargs["ip"]
        ap = get_object_or_404(AccessPoint, main_ip=ip)
        return ap.get_links()


class AccessPointInterfacesList(generics.ListAPIView):
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
