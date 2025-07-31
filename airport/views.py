from datetime import timedelta

from django.db import transaction
from django.utils.timezone import now
from drf_spectacular.utils import extend_schema
from rest_framework import viewsets, status, permissions, mixins
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from airport.models import AirplaneType, Airplane, Crew, Airport, Route, Flight, Order
from airport.permissions import IsAdminOrAuthenticatedReadOnly
from airport.serializers import AirplaneTypeSerializer, AirplaneListSerializer, AirplaneEditSerializer, \
    AirplaneImageSerializer, CrewSerializer, AirportSerializer, RouteListSerializer, RouteDetailSerializer, \
    RouteSerializer, FLightListSerializer, FlightDetailSerializer, FlightSerializer, OrderCreateSerializer, \
    OrderSerializer, OrderDetailSerializer, ReturnBalanceSerializer
from django.utils.translation import gettext as _


@extend_schema(tags=["Airplane Type"])
class AirplaneTypeViewSet(viewsets.ModelViewSet):
    queryset = AirplaneType.objects.all()
    serializer_class = AirplaneTypeSerializer
    permission_classes = (IsAdminOrAuthenticatedReadOnly,)


@extend_schema(tags=["Airplane"])
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


@extend_schema(tags=["Crew"])
class CrewViewSet(viewsets.ModelViewSet):
    queryset = Crew.objects.all()
    serializer_class = CrewSerializer
    permission_classes = (IsAdminOrAuthenticatedReadOnly,)


@extend_schema(tags=["Airport"])
class AirportViewSet(viewsets.ModelViewSet):
    queryset = Airport.objects.all()
    serializer_class = AirportSerializer
    permission_classes = (IsAdminOrAuthenticatedReadOnly,)


@extend_schema(tags=["Routes"])
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


@extend_schema(tags=["Flights"])
class FlightViewSet(viewsets.ModelViewSet):
    queryset = Flight.objects.all()
    permission_classes = (IsAdminOrAuthenticatedReadOnly,)

    def get_serializer_class(self):
        if self.action == "list":
            return FLightListSerializer
        elif self.action == "retrieve":
            return FlightDetailSerializer
        return FlightSerializer


@extend_schema(tags=["Orders"])
class OrderViewSet(mixins.CreateModelMixin,
                      mixins.RetrieveModelMixin,
                      mixins.ListModelMixin,
                      GenericViewSet):
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        user = self.request.user
        queryset = Order.objects.all().filter(user=user)
        return queryset

    def get_serializer_class(self):
        if self.action == "create":
            return OrderCreateSerializer
        if self.action == "retrieve":
            return OrderDetailSerializer
        if self.action == "cancel":
            return ReturnBalanceSerializer
        return OrderSerializer

    @extend_schema(request=None, responses=ReturnBalanceSerializer)
    @action(detail=True, methods=["post"], url_name="cancel")
    def cancel(self, request, pk=None):
        order = self.get_object()
        today = now().date()
        user = order.user
        created_date = order.created_at.date()
        if created_date + timedelta(days=14) < today:
            return Response({"detail": _("Order older than 14 days cannot be cancelled")}, status=status.HTTP_403_FORBIDDEN)
        if order.tickets.all().count() < 1:
            return Response({"detail": _("No tickets available")}, status=status.HTTP_403_FORBIDDEN)
        with transaction.atomic():
            return_balance = 0
            not_returnable = []
            for ticket in order.tickets.all():
                if ticket.flight.status != "PLANNED":
                    not_returnable.append(ticket)
                    continue
                else:
                    return_balance += ticket.price
                    ticket.delete()
            user.balance = user.balance + return_balance
            user.save()
        data = {
            "tickets": not_returnable,
            "returned_balance": return_balance,
            "balance": user.balance,
        }
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

