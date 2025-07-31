from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from drf_spectacular.views import (
    SpectacularYAMLAPIView,
    SpectacularJSONAPIView,
    SpectacularSwaggerView,
    SpectacularRedocView
)

from airport_api import settings

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/v1/", include("airport.urls", namespace="airport")),
    path("api/v1/user/", include("user.urls", namespace="user")),
]


if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += [path("yml/", SpectacularYAMLAPIView.as_view(), name="yml-schema")]
    urlpatterns += [path("json/", SpectacularJSONAPIView.as_view(), name="schema")]
    urlpatterns += [
        path("swagger/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui")
    ]
    urlpatterns += [path("redoc/", SpectacularRedocView.as_view(), name="redoc")]
    import debug_toolbar
    urlpatterns += [path('__debug__/', include(debug_toolbar.urls))]
