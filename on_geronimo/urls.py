from django.conf.urls import include, url
from django.contrib import admin
from django.views.generic import TemplateView


urlpatterns = [
    # Examples:
    # url(r"^$", "gero_api.views.home", name="home"),
    # url(r"^blog/", include("blog.urls")),

    url(r"^api/", include("on_geronimo.oni_model.urls")),
    url(r"^admin/", admin.site.urls),
    url(r"^$", TemplateView.as_view(template_name="examples.html"), name="examples"),
]
