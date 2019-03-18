from django.conf.urls import url
from django.views.decorators.cache import cache_page

from . import views


ap_path_prefix = r"^v1/accesspoint/(?P<pk>(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}))"
iface_path_prefix = r"^v1/interface/(?P<addresses__address>(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}))"


urlpatterns = [
    url(r"^v1/accesspoint/$", views.AccessPointList.as_view()),
    url(ap_path_prefix + "$", views.AccessPointDetail.as_view()),
    url(ap_path_prefix + "/interfaces/$", views.AccessPointInterfacesDetail.as_view()),
    url(ap_path_prefix + "/links/$", views.AccessPointLinksDetail.as_view()),
    url(r"^v1/interface/$", views.AccessPointInterfacesList.as_view()),
    url(iface_path_prefix + "$", views.NetworkInterfaceDetail.as_view()),
    url(iface_path_prefix + "/accesspoint/$", views.NetworkInterfaceAccessPoint.as_view()),
    url(r'^v1/link/$', cache_page(150)(views.AccessPointLinksList.as_view())),
    url(r'^v1/site/$', views.AccessPointSiteList.as_view()),
    url(r'^v1/site/(?P<pk>\d+)$', views.AccessPointSiteDetail.as_view()),
]
