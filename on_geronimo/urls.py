from django.urls import include, re_path
from django.contrib import admin
from django.views.generic import TemplateView


urlpatterns = [
    # Examples:
    # re_path(r"^$", "gero_api.views.home", name="home"),
    # re_path(r"^blog/", include("blog.urls")),

    re_path(r"^api/", include("on_geronimo.oni_model.urls")),
    re_path(r"^admin/", admin.site.urls),
    re_path(r"^$", TemplateView.as_view(template_name="examples.html"), name="examples"),
]
