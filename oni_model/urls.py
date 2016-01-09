from django.conf.urls import patterns, include, url
from oni_model import views

v1_urlpatterns = patterns('',
        url(r'^accesspoint/$', views.AccessPointList.as_view()),
        url(r'^accesspoint/(?P<pk>(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}))$', views.AccessPointDetail.as_view()),
        url(r'^link/$', views.AccessPointLinksList.as_view()),
        url(r'^accesspoint/(?P<ip>(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}))/links/$', views.AccessPointLinksDetail.as_view()),
        url(r'^interface/(?P<ip_address>(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}))/accesspoint/$', views.NetworkInterfaceAccessPoint.as_view()),
        url(r'^interface/(?P<ip_address>(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}))$', views.NetworkInterfaceDetail.as_view()),
        url(r'^interface/$', views.AccessPointInterfacesList.as_view()),
        url(r'^accesspoint/(?P<ip>(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}))/interfaces/$', views.AccessPointInterfacesDetail.as_view()),
        )

urlpatterns = patterns('',
        url(r'v1/', include(v1_urlpatterns)),
        )
