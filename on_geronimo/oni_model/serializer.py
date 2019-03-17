from rest_framework_gis import serializers

from on_geronimo.oni_model.models import (
    AccessPoint, AccessPointSite, InterfaceRoutingLink, RoutingLink, EthernetNetworkInterface,
    NetworkInterfaceAddress, WifiNetworkInterfaceAttributes)


class AccessPointSiteSerializer(serializers.GeoModelSerializer):

    class Meta:
        model = AccessPointSite
        fields = ("accesspoints", "post_address")


class AccessPointSerializer(serializers.GeoModelSerializer):

    class Meta:
        model = AccessPoint


class WifiNetworkInterfaceAttributesSerializer(serializers.ModelSerializer):

    class Meta:
        model = WifiNetworkInterfaceAttributes


class NetworkInterfaceAddressSerializer(serializers.ModelSerializer):

    class Meta:
        model = NetworkInterfaceAddress


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
