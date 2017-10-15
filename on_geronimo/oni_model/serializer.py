from rest_framework_gis import serializers

from on_geronimo.oni_model.models import (AccessPoint, InterfaceRoutingLink, RoutingLink,
                                          EthernetNetworkInterface, WifiNetworkInterfaceAttributes)


class AccessPointSerializer(serializers.GeoModelSerializer):

    class Meta:
        model = AccessPoint


class WifiNetworkInterfaceAttributesSerializer(serializers.ModelSerializer):

    class Meta:
        model = WifiNetworkInterfaceAttributes


class EthernetNetworkInterfaceSerializer(serializers.ModelSerializer):

    wifi_attributes = WifiNetworkInterfaceAttributesSerializer(many=True, read_only=True)

    class Meta:
        model = EthernetNetworkInterface
        fields = ("ip_address", "if_name", "is_wireless", "wifi_attributes")


class InterfaceRoutingLinkSerializer(serializers.ModelSerializer):

    interface = EthernetNetworkInterfaceSerializer()

    class Meta:
        model = InterfaceRoutingLink
        fields = ("quality", "interface")


class RoutingLinkSerializer(serializers.ModelSerializer):

    endpoints = InterfaceRoutingLinkSerializer(many=True, read_only=True)

    class Meta:
        model = RoutingLink
        fields = ("endpoints", "timestamp", "position", "quality", "wifi_ssid")
