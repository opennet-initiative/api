from django.shortcuts import render, get_object_or_404

from oni_model.models import AccessPoint, RoutingLink, EthernetNetworkInterface, InterfaceRoutingLink
from oni_model.serializer import AccessPointSerializer, RoutingLinkSerializer, InterfaceRoutingLinkSerializer

from rest_framework import mixins
from rest_framework import filters
from rest_framework import generics
from rest_framework.views import APIView
from rest_framework.response import Response


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
    queryset = AccessPoint.objects.all()
    serializer_class = AccessPointSerializer


class AccessPointDetail(DetailView):
    """Liefert die Details eines WLAN Accesspoints des Opennets"""
    queryset = AccessPoint.objects.all()
    serializer_class = AccessPointSerializer
    
class LinkList(ListView):
    """Liefert eine Liste aller Links zwischen Accesspoints des Opennets"""
    queryset = RoutingLink.objects.all()
    serializer_class = RoutingLinkSerializer

class LinkDetail(ListView):
    """Alle Links zu diesem WLAN Accesspoints des Opennets"""
    
    def get_queryset(self):
        print(self.args)
        ip=self.kwargs["ip"]
        self.ap = AccessPoint.objects.get(main_ip=ip)
        ifs=EthernetNetworkInterface.objects.filter(access_point=self.ap)
        iflinks=InterfaceRoutingLink.objects.filter(interface=ifs)
        #rlinks = RoutingLink.objects.filter(endpoints=iflinks[0].routing_link)
        return iflinks
    
    #queryset = AccessPoint.objects.all()
    serializer_class = InterfaceRoutingLinkSerializer