from django.conf.urls import url

from geronimo.oni_model import views


urlpatterns = [
    url(r'^v1/accesspoint/$', views.AccessPointList.as_view()),
    url(r'^v1/accesspoint/(?P<pk>(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}))$',
        views.AccessPointDetail.as_view()),
    url(r'^v1/link/$', views.AccessPointLinksList.as_view()),
    url(r'^v1/accesspoint/(?P<ip>(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}))/links/$',
        views.AccessPointLinksDetail.as_view()),
    url(r'^v1/interface/(?P<ip_address>(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}))/accesspoint/$',
        views.NetworkInterfaceAccessPoint.as_view()),
    url(r'^v1/interface/(?P<ip_address>(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}))$',
        views.NetworkInterfaceDetail.as_view()),
    url(r'^v1/interface/$', views.AccessPointInterfacesList.as_view()),
    url(r'^v1/accesspoint/(?P<ip>(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}))/interfaces/$',
        views.AccessPointInterfacesDetail.as_view()),
]
