from django.core.exceptions import SuspiciousOperation
from django.http import Http404
from django.shortcuts import get_object_or_404
from rest_framework import generics
from rest_framework import mixins
from rest_framework.filters import BaseFilterBackend
from rest_framework.response import Response
from rest_framework_gis.fields import GeometryField
from rest_framework_gis.filters import InBBoxFilter
from rest_framework_gis.serializers import GeoFeatureModelSerializer

from .models import (AccessPoint, AccessPointSite, EthernetNetworkInterface, InterfaceRoutingLink,
                     RoutingLink)
from .serializer import (AccessPointSerializer, AccessPointSiteSerializer, RoutingLinkSerializer,
                         EthernetNetworkInterfaceSerializer)


class DetailView(mixins.RetrieveModelMixin,
                 generics.GenericAPIView):

    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    # make this an uninstanceable class
    class Meta:
        abstract = True


class AccessPointMixin:
    """ allow the selection of an accesspoint with either its IPv4 or IPv6 address """

    # allow multiple primary keys for selecting an accesspoint
    # These keys must be used as pattern names in the URL specification.
    lookup_fields = ("main_ipv6", "main_ip")

    def get_accesspoint(self):
        key = self.lookup_field
        value = self.kwargs.get(self.lookup_field)
        if value is None:
            raise Http404
        obj = get_object_or_404(AccessPoint.objects, **{key: value})
        self.check_object_permissions(self.request, obj)
        return obj

    @property
    def lookup_field(self):
        for lookup_field in self.lookup_fields:
            if self.kwargs.get(lookup_field) is not None:
                break
        return lookup_field

    @property
    def lookup_kwarg(self):
        return self.lookup_field


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
        wanted_format = self.request.query_params.get("data_format", None)
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
                                pk=iface_link_id).interface.accesspoint.main_ip
                    return result

            return GeoSerializer
        else:
            return self.serializer_class


class OnlineStatusFilter(BaseFilterBackend):
    """ filter objects by the a timestamp attribute into all/online/flapping/offline categories

    Query arguments:
        * status: all/online/flapping/offline
    """

    def filter_queryset(self, request, queryset, view):
        wanted_status = request.query_params.get("status", "online")
        if wanted_status == "all":
            # This set contains all objects without a timestamp (e.g. accesspoints that went
            # offline before the API started to collect data.
            return queryset
        elif wanted_status == "online":
            return queryset.model.online_objects.filter_by_status(queryset)
        elif wanted_status == "offline":
            return queryset.model.offline_objects.filter_by_status(queryset)
        elif wanted_status == "flapping":
            return queryset.model.flapping_objects.filter_by_status(queryset)
        else:
            return queryset.none()


class FirmwareVersionFilter(BaseFilterBackend):

    def filter_queryset(self, request, queryset, view):
        version_queryset = queryset.model.firmware_version_objects
        wanted_version = request.query_params.get("firmware_version")
        # allow filtering for "no version set" (empty string)
        if wanted_version is not None:
            queryset = version_queryset.is_version(queryset, wanted_version or None)
        before_version = request.query_params.get("firmware_version__before")
        if before_version:
            queryset = version_queryset.before_version(queryset, before_version)
        after_version = request.query_params.get("firmware_version__after")
        if after_version:
            queryset = version_queryset.after_version(queryset, after_version)
        return queryset


class LinkAccessPointInBBoxFilter(InBBoxFilter):
    """ filter links based on a bounding box

    Only links referring to at least one AccessPoint within the given bounding box are returned.
    """

    def filter_queryset(self, request, queryset, view):
        bbox = self.get_filter_bbox(request)
        if not bbox:
            return queryset
        else:
            return (queryset.filter(endpoints__interface__accesspoint__position__contained=bbox)
                    .distinct().prefetch_related("endpoints"))


class AccessPointSiteList(GeoJSONListAPIView):
    """ Liefert eine Liste aller WLAN Accesspoints des Opennets """

    serializer_class = AccessPointSiteSerializer
    geojson_base_model = AccessPointSite
    geojson_serializer_extra_fields = {"position"}
    bbox_filter_field = "position"
    filter_backends = (InBBoxFilter, )
    queryset = AccessPointSite.objects.all()


class AccessPointSiteDetail(DetailView):
    """Liefert die Details eines WLAN Accesspoints des Opennets"""

    queryset = AccessPointSite.objects.all()
    serializer_class = AccessPointSiteSerializer


class AccessPointList(GeoJSONListAPIView):
    """ Liefert eine Liste aller WLAN Accesspoints des Opennets """

    serializer_class = AccessPointSerializer
    geojson_base_model = AccessPoint
    # The map relies on the primary key ("main_ip") being available. GeoJSON would skip the
    # primary key, if it is not mentioned separately.
    geojson_serializer_extra_fields = ["main_ip"]
    geojson_serializer_ignore_fields = ["interfaces"]
    bbox_filter_field = "position"
    filter_backends = (OnlineStatusFilter, FirmwareVersionFilter, InBBoxFilter)
    queryset = AccessPoint.objects.all()


class AccessPointDetail(AccessPointMixin, DetailView):
    """Liefert die Details eines WLAN Accesspoints des Opennets"""

    queryset = AccessPoint.objects.all()
    serializer_class = AccessPointSerializer


class ExcludeSite2SiteLinks(BaseFilterBackend):
    """ Remove all RoutingLink objects that are part of an inter-site connection

    An inter-site connection satisfies the following conditions:
        * both ends of the link are part of a (different) site
        * the two connected sides have more than one direct connection
    """

    def _get_redundantly_connected_sites(self):
        site_pairs_count = {}
        for link in RoutingLink.online_objects.exclude(
                endpoints__interface__accesspoint__site__isnull=True):
            pair = tuple(sorted(endpoint.interface.accesspoint.site.id
                                for endpoint in link.endpoints.all()))
            if len(pair) != 2:
                # remove a broken (partially deleted) link
                link.delete()
            else:
                # only use connections between different sites
                if pair[0] != pair[1]:
                    try:
                        site_pairs_count[pair] += 1
                    except KeyError:
                        site_pairs_count[pair] = 1
        return {pair for pair, count in site_pairs_count.items() if count > 1}

    def filter_queryset(self, request, queryset, view):
        if request.GET.get("with_redundant_site_links", "1") == "0":
            ignored_routing_links = set()
            for pair in self._get_redundantly_connected_sites():
                first, second = pair
                ignored_routing_links.update(link.id for link in (
                    RoutingLink.objects
                    .filter(endpoints__interface__accesspoint__site__id=first)
                    .filter(endpoints__interface__accesspoint__site__id=second)))
            queryset = queryset.exclude(pk__in=ignored_routing_links)
        return queryset


class RoutingLinkList(GeoJSONListAPIView):
    """Liefert eine Liste aller Links zwischen Accesspoints des Opennets"""

    serializer_class = RoutingLinkSerializer
    geojson_base_model = RoutingLink
    # we need to add non-fields (properties) manually
    geojson_serializer_extra_fields = {"quality", "wifi_ssid", "is_wireless"}
    filter_backends = (OnlineStatusFilter, LinkAccessPointInBBoxFilter, ExcludeSite2SiteLinks)
    queryset = RoutingLink.objects.all()


class AccessPointLinkDetail(AccessPointMixin, generics.ListAPIView):
    """Alle Links zu diesem WLAN Accesspoints des Opennets"""

    serializer_class = RoutingLinkSerializer
    filter_backends = (OnlineStatusFilter, )

    def get_queryset(self):
        ap = self.get_accesspoint()
        return ap.get_links()


class AccessPointInterfacesList(generics.ListAPIView):
    """Liefert eine Liste aller Interfaces von Accesspoints des Opennets"""

    serializer_class = EthernetNetworkInterfaceSerializer

    def get_queryset(self):
        queryset = EthernetNetworkInterface.objects.all()
        if self.request.GET.get("if_hwaddress"):
            queryset = queryset.filter(if_hwaddress__iexact=self.request.GET.get("if_hwaddress"))
        if self.request.GET.get("wifi_ssid"):
            queryset = queryset.filter(
                wifi_attributes__wifi_ssid=self.request.GET.get("wifi_ssid"))
        if self.request.GET.get("is_wireless"):
            if self.request.GET.get("is_wireless").lower() in {"true", "1"}:
                queryset = queryset.exclude(wifi_attributes=None)
            elif self.request.GET.get("is_wireless").lower() in {"false", "0"}:
                queryset = queryset.filter(wifi_attributes=None)
            else:
                raise SuspiciousOperation("Invalid boolean value requested ('{}') - expected one "
                                          "of: true / false / 1 / 0"
                                          .format(self.request.GET.get("is_wireless")))
        return queryset


class NetworkInterfaceDetail(DetailView):
    """Ein Interface mit einer spezifischen IP"""

    lookup_field = "addresses__address"
    queryset = EthernetNetworkInterface.objects.all()
    serializer_class = EthernetNetworkInterfaceSerializer


class NetworkInterfaceAccessPoint(DetailView):
    """Der AP der zu einer IP gehoert"""

    serializer_class = AccessPointSerializer

    def retrieve(self, request, **kwargs):
        interface = get_object_or_404(EthernetNetworkInterface, **kwargs)
        return Response(self.serializer_class(interface.accesspoint).data)


class AccessPointInterfacesDetail(AccessPointMixin,
                                  mixins.ListModelMixin,
                                  generics.GenericAPIView):
    """Alle Interfaces eines Accesspoints des Opennets"""

    serializer_class = EthernetNetworkInterfaceSerializer

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    def get_queryset(self):
        ap = self.get_accesspoint()
        return ap.interfaces
