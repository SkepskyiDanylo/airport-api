from django.urls import path, include
from rest_framework.routers import DefaultRouter

from airport.views import AirplaneTypeViewSet

router = DefaultRouter()
router.register("airplane-types", AirplaneTypeViewSet, basename="airplane-type")


urlpatterns = [
    path("", include(router.urls)),
]


app_name = "airport"