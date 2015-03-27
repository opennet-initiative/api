from django.conf.urls import patterns, include, url
from oni_model import views

v1_urlpatterns = patterns('',
        url(r'^accesspoint/$', views.AccessPointList.as_view()),
        )

urlpatterns = patterns('',
        url(r'v1/', include(v1_urlpatterns)),
        )
