from requests import Response
from rest_framework import viewsets, status
from rest_framework.decorators import action

from airport.models import AirplaneType, Airplane, Crew, Airport, Route, Flight
from airport.permissions import IsAdminOrAuthenticatedReadOnly
from airport.serializers import AirplaneTypeSerializer, AirplaneListSerializer, AirplaneEditSerializer, \
    AirplaneImageSerializer, CrewSerializer, AirportSerializer, RouteListSerializer, RouteDetailSerializer, \
    RouteSerializer, FLightListSerializer, FlightDetailSerializer, FlightSerializer


class AirplaneTypeViewSet(viewsets.ModelViewSet):
    queryset = AirplaneType.objects.all()
    serializer_class = AirplaneTypeSerializer
    permission_classes = (IsAdminOrAuthenticatedReadOnly,)


class AirplaneViewSet(viewsets.ModelViewSet):
    queryset = Airplane.objects.all()
    permission_classes = (IsAdminOrAuthenticatedReadOnly,)

    def get_queryset(self):
        queryset = Airplane.objects.all().select_related("type")
        model = self.request.GET.get("model", None)
        airplane_status = self.request.GET.get("status", None)
        manufacturer = self.request.GET.get("manufacturer", None)

        if model:
            queryset = queryset.filter(model__icontains=model)
        if airplane_status:
            queryset = queryset.filter(status__icontains=airplane_status)
        if manufacturer:
            queryset = queryset.filter(manufacturer__icontains=manufacturer)
        return queryset

    def get_serializer_class(self):
        if self.action in ("list", "retrieve"):
            return AirplaneListSerializer
        if self.action == "set-image":
            return AirplaneImageSerializer
        return AirplaneEditSerializer

    @action(detail=True, methods=["post"], url_name="set-image")
    def set_image(self, request, pk=None):
        instance = self.get_object()
        data = request.data
        serializer = self.get_serializer(instance, data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)


class CrewViewSet(viewsets.ModelViewSet):
    queryset = Crew.objects.all()
    serializer_class = CrewSerializer
    permission_classes = (IsAdminOrAuthenticatedReadOnly,)


class AirportViewSet(viewsets.ModelViewSet):
    queryset = Airport.objects.all()
    serializer_class = AirportSerializer
    permission_classes = (IsAdminOrAuthenticatedReadOnly,)


class RouteViewSet(viewsets.ModelViewSet):
    queryset = Route.objects.all()
    permission_classes = (IsAdminOrAuthenticatedReadOnly,)

    def get_queryset(self):
        queryset = Route.objects.all().select_related("source", "destination")
        queryset = queryset.prefetch_related("stops")
        destination = self.request.GET.get("destination", None)
        source = self.request.GET.get("source", None)
        stops = self.request.GET.get("stops", None)
        if destination:
            queryset = queryset.filter(destination__name__icontains=destination)
        if source:
            queryset = queryset.filter(source__name__icontains=source)
        if stops:
            stop_list = [s.strip() for s in stops.split(",") if s.strip()]
            queryset = queryset.filter(stops__name__in=stop_list)
        return queryset.distinct()

    def get_serializer_class(self):
        if self.action == "list":
            return RouteListSerializer
        if self.action == "retrieve":
            return RouteDetailSerializer
        return RouteSerializer


class FlightViewSet(viewsets.ModelViewSet):
    queryset = Flight.objects.all()
    permission_classes = (IsAdminOrAuthenticatedReadOnly,)

    def get_serializer_class(self):
        if self.action == "list":
            return FLightListSerializer
        elif self.action == "retrieve":
            return FlightDetailSerializer
        return FlightSerializer