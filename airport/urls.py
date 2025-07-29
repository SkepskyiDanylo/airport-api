from django.urls import path, include
from rest_framework.routers import DefaultRouter

from airport.views import AirplaneTypeViewSet, AirplaneViewSet, RouteViewSet, CrewViewSet, AirportViewSet, FlightViewSet


router = DefaultRouter()
router.register("airplane-types", AirplaneTypeViewSet, basename="airplane-type")
router.register("airplanes", AirplaneViewSet, basename="airplane")
router.register("crew", CrewViewSet, basename="crew")
router.register("airports", AirportViewSet, basename="airport")
router.register("routes", RouteViewSet, basename="route")
router.register("flights", FlightViewSet, basename="flight")


urlpatterns = [
    path("", include(router.urls)),
]


app_name = "airport"