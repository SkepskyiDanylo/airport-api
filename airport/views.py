from requests import Response
from rest_framework import viewsets, status
from rest_framework.decorators import action

from airport.models import AirplaneType, Airplane
from airport.permissions import IsAdminOrAuthenticatedReadOnly
from airport.serializers import AirplaneTypeSerializer, AirplaneListSerializer, AirplaneEditSerializer, \
    AirplaneImageSerializer


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
