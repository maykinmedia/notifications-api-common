from django.contrib import admin
from django.urls import include, path

from .api import router
from .views import KanalenView

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include(router.urls)),
    path(
        "notificaties/",
        include(
            (
                [path("kanalen/", KanalenView.as_view(), name="kanalen")],
                "notifications",
            ),
            namespace="notifications",
        ),
    ),
]
