from django.conf.urls import url
from django.views.decorators.cache import cache_page

from . import views


REGEX_PATTERNS = {
    "ipv4": r"(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})",
    "ipv6": r"[0-9a-fA-F:]+",
}
ap_path_prefix = (r"^v1/accesspoint/((?P<main_ip>{ipv4})|(?P<main_ipv6>{ipv6}))"
                  .format(**REGEX_PATTERNS))
iface_path_prefix = r"^v1/interface/(?P<addresses__address>{ipv4}|{ipv6})".format(**REGEX_PATTERNS)


urlpatterns = [
    url(r"^v1/accesspoint/$", views.AccessPointList.as_view(), name="accesspoint-list"),
    url(ap_path_prefix + "$", views.AccessPointDetail.as_view(), name="accesspoint-details"),
    url(ap_path_prefix + "/interfaces/$", views.AccessPointInterfacesDetail.as_view(),
        name="accesspoint-interfaces"),
    url(ap_path_prefix + "/links/$", views.AccessPointLinkDetail.as_view(),
        name="accesspoint-links"),
    url(r"^v1/interface/$", views.AccessPointInterfacesList.as_view(), name="interface-list"),
    url(iface_path_prefix + "$", views.NetworkInterfaceDetail.as_view(), name="interface-details"),
    url(iface_path_prefix + "/accesspoint/$", views.NetworkInterfaceAccessPoint.as_view(),
        name="interface-accesspoint"),
    url(r"^v1/link/$", cache_page(150)(views.RoutingLinkList.as_view()), name="link-list"),
    url(r"^v1/link/(?P<pk>\d+)$", views.AccessPointLinkDetail.as_view(), name="link-details"),
    url(r"^v1/site/$", views.AccessPointSiteList.as_view(), name="site-list"),
    url(r"^v1/site/(?P<pk>\d+)$", views.AccessPointSiteDetail.as_view(), name="site-details"),
]
