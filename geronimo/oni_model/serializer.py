from rest_framework import serializers
from oni_model.models import AccessPoint, InterfaceRoutingLink, RoutingLink, EthernetNetworkInterface

class AccessPointSerializer(serializers.ModelSerializer):
    class Meta:
        model = AccessPoint

class EthernetNetworkInterfaceSerializer(serializers.ModelSerializer):
    class Meta:
        model = EthernetNetworkInterface
        fields = ("ip_address", "if_name")
        
class InterfaceRoutingLinkSerializer(serializers.ModelSerializer):
    interface = EthernetNetworkInterfaceSerializer()
    class Meta:
        model = InterfaceRoutingLink
        fields = ("quality", "interface")
        
class RoutingLinkSerializer(serializers.ModelSerializer):
    endpoints = InterfaceRoutingLinkSerializer(many=True, read_only=True)
    class Meta:
        model = RoutingLink
