from django.shortcuts import render

from oni_model.models import AccessPoint, InterfaceRoutingLink
from oni_model.serializer import AccessPointSerializer, LinkSerializer

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
    queryset = InterfaceRoutingLink.objects.all()
    serializer_class = LinkSerializer
