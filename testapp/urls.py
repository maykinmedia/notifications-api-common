from django.contrib import admin
from django.urls import include, path
from django.views import View

from .api import router

notifications_patterns = [
    path("kanalen/", View.as_view(), name="kanalen"),
]


urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include(router.urls)),
    path(
        "notifications/",
        include((notifications_patterns, "notifications"), namespace="notifications"),
    ),
]
