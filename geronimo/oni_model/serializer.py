from rest_framework import serializers
from oni_model.models import AccessPoint, InterfaceRoutingLink, RoutingLink, EthernetNetworkInterface

class AccessPointSerializer(serializers.ModelSerializer):
    class Meta:
        model = AccessPoint
        
class RoutingLinkSerializer(serializers.ModelSerializer):
    class Meta:
        model = RoutingLink

class EthernetNetworkInterfaceSerializer(serializers.ModelSerializer):
    class Meta:
        model = EthernetNetworkInterface
        fields = ("ip_address",)
        
class LinkSerializer(serializers.ModelSerializer):
    interface=EthernetNetworkInterfaceSerializer()
    routing_link=RoutingLinkSerializer()
    class Meta:
        model = InterfaceRoutingLink