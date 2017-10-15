import datetime

from django.shortcuts import get_object_or_404
from rest_framework import generics
from rest_framework import mixins
from rest_framework.filters import BaseFilterBackend
from rest_framework.response import Response
from rest_framework_gis.fields import GeometryField
from rest_framework_gis.filters import InBBoxFilter
from rest_framework_gis.serializers import GeoFeatureModelSerializer

from on_geronimo.oni_model.models import (
    AccessPoint, EthernetNetworkInterface, InterfaceRoutingLink, RoutingLink)
from on_geronimo.oni_model.serializer import (
    AccessPointSerializer, RoutingLinkSerializer, EthernetNetworkInterfaceSerializer)


# nach dreißig Tagen gelten APs nicht mehr als "flapping", sondern als "offline"
# Vorsicht: Werte synchron halten mit der "flapping"-Unterscheidung im der on-map-Kartendarstellung
OFFLINE_AGE_MINUTES = 30 * 24 * 60
FLAPPING_AGE_MINUTES = 30


class DetailView(mixins.RetrieveModelMixin,
                 mixins.UpdateModelMixin,
                 generics.GenericAPIView):

    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    # make this an uninstanceable class
    class Meta:
        abstract = True


class GeoJSONListAPIView(generics.ListAPIView):
    """ select a GeoJSON serializer if the query argument 'data_format' is 'geojson'

    Query arguments:
        * data_format: "geojson" or something else
    Attributes:
        * geojson_base_model: the django model of the objects to be rendered
        * geojson_serializer_extra_fields: list of additional fields to be copied to the feature
          properties (besides the fields of the base model)
        * serializer_class: the fallback serialer class (to be used if geojson is not requested)
    """

    def get_serializer_class(self):
        wanted_format = self.request.query_params.get('data_format', None)
        if wanted_format == "geojson":
            feature_fields = []
            ignore_fields = getattr(self, "geojson_serializer_ignore_fields", [])
            for field in self.geojson_base_model._meta.get_fields():
                if field.name not in ignore_fields:
                    feature_fields.append(field.name)
            feature_fields.extend(self.geojson_serializer_extra_fields)

            class GeoSerializer(GeoFeatureModelSerializer):
                class Meta:
                    model = self.geojson_base_model
                    geo_field = "position"
                    fields = feature_fields
                    # We do not want GeoFeatureModelSerializer to "consume" the "main_ip" field
                    # while filling the (unnecessary) "id" attribute.
                    id_field = None

                def to_representation(self, instance):
                    result = super().to_representation(instance)
                    if not isinstance(result["geometry"], dict):
                        # The "position" was just dumped (being a stupid property). We need to
                        # turn it into the geojson format.
                        position = getattr(instance, self.Meta.geo_field)
                        if position:
                            result["geometry"] = GeometryField().to_representation(position)
                    # replace numeric AccessPoint IDs with "main_ip"
                    if "endpoints" in result["properties"]:
                        endpoints = result["properties"]["endpoints"]
                        for index, iface_link_id in enumerate(endpoints):
                            endpoints[index] = InterfaceRoutingLink.objects.get(
                                pk=iface_link_id).interface.access_point.main_ip
                    return result

            return GeoSerializer
        else:
            return self.serializer_class


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


class AccessPointList(GeoJSONListAPIView):
    """ Liefert eine Liste aller WLAN Accesspoints des Opennets """

    serializer_class = AccessPointSerializer
    geojson_base_model = AccessPoint
    # The map relies on the primary key ("main_ip") being available. GeoJSON would skip the
    # primary key, if it is not mentioned separately.
    geojson_serializer_extra_fields = ["main_ip"]
    geojson_serializer_ignore_fields = ["interfaces"]
    bbox_filter_field = 'position'
    filter_backends = (InBBoxFilter, OnlineStatusFilter)
    queryset = AccessPoint.objects.all()
    last_online_timestamp_field = "lastseen_timestamp"


class AccessPointDetail(DetailView):
    """Liefert die Details eines WLAN Accesspoints des Opennets"""

    queryset = AccessPoint.objects.all()
    serializer_class = AccessPointSerializer


class AccessPointLinksList(GeoJSONListAPIView):
    """Liefert eine Liste aller Links zwischen Accesspoints des Opennets"""

    serializer_class = RoutingLinkSerializer
    geojson_base_model = RoutingLink
    # we need to add non-fields (properties) manually
    geojson_serializer_extra_fields = ["quality", "wifi_ssid", "is_wireless"]
    filter_backends = (OnlineStatusFilter, )
    queryset = RoutingLink.objects.all()


class AccessPointLinksDetail(generics.ListAPIView):
    """Alle Links zu diesem WLAN Accesspoints des Opennets"""

    serializer_class = RoutingLinkSerializer
    filter_backends = (OnlineStatusFilter, )

    def get_queryset(self):
        ip = self.kwargs["pk"]
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


class AccessPointInterfacesDetail(mixins.ListModelMixin,
                                  mixins.CreateModelMixin,
                                  generics.GenericAPIView):
    """Alle Interfaces eines Accesspoints des Opennets"""

    serializer_class = EthernetNetworkInterfaceSerializer

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    def retrieve(self, request, ip_address=None):
        ap = get_object_or_404(AccessPoint, main_ip=ip_address)
        return Response(self.serializer_class(ap.interfaces).data)
