from rest_framework_gis import serializers 
from oni_model.models import AccessPoint


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
        fields = ("ip_address", "if_name", "wifi_attributes")


class InterfaceRoutingLinkSerializer(serializers.ModelSerializer):
    interface = EthernetNetworkInterfaceSerializer()
    class Meta:
        model = InterfaceRoutingLink
        fields = ("quality", "interface")


class RoutingLinkSerializer(serializers.ModelSerializer):
    endpoints = InterfaceRoutingLinkSerializer(many=True, read_only=True)
    class Meta:
        model = RoutingLink
