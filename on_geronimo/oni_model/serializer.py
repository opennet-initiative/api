from rest_framework_gis import serializers
from rest_framework_gis.fields import GeometryField

from on_geronimo.oni_model.models import (
    AccessPoint, AccessPointSite, InterfaceRoutingLink, RoutingLink, EthernetNetworkInterface,
    NetworkInterfaceAddress, WifiNetworkInterfaceAttributes)


class AccessPointSiteSerializer(serializers.GeoModelSerializer):

    position = GeometryField()

    class Meta:
        model = AccessPointSite
        fields = ("accesspoints", "id", "position", "post_address")


class AccessPointSerializer(serializers.GeoModelSerializer):

    class Meta:
        model = AccessPoint
        fields = "__all__"


class WifiNetworkInterfaceAttributesSerializer(serializers.ModelSerializer):

    class Meta:
        model = WifiNetworkInterfaceAttributes
        fields = "__all__"


class NetworkInterfaceAddressSerializer(serializers.ModelSerializer):

    class Meta:
        model = NetworkInterfaceAddress
        fields = "__all__"


class EthernetNetworkInterfaceSerializer(serializers.ModelSerializer):

    wifi_attributes = WifiNetworkInterfaceAttributesSerializer(many=True, read_only=True)
    addresses = NetworkInterfaceAddressSerializer(many=True, read_only=True)

    class Meta:
        model = EthernetNetworkInterface
        fields = ("addresses", "if_name", "if_hwaddress", "is_wireless", "wifi_attributes",
                  "accesspoint")


class InterfaceRoutingLinkSerializer(serializers.ModelSerializer):

    interface = EthernetNetworkInterfaceSerializer()

    class Meta:
        model = InterfaceRoutingLink
        fields = ("quality", "interface")


class RoutingLinkSerializer(serializers.ModelSerializer):

    endpoints = InterfaceRoutingLinkSerializer(many=True, read_only=True)

    class Meta:
        model = RoutingLink
        fields = ("endpoints", "timestamp", "position", "quality", "wifi_ssid", "is_wireless")
