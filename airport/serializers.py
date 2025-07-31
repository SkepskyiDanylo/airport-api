from decimal import Decimal

from django.db import transaction
from rest_framework import serializers
from airport.models import AirplaneType, Airplane, Crew, Airport, Route, Flight, Ticket, Order
from django.utils.translation import gettext_lazy as _


class AirplaneTypeSerializer(serializers.ModelSerializer):

    class Meta:
        model = AirplaneType
        fields = (
            "id",
            "name",
        )


class AirplaneListSerializer(serializers.ModelSerializer):
    type_name = serializers.CharField(
        source="type.name",
    )

    class Meta:
        model = Airplane
        fields = (
            "id",
            "tail_number",
            "manufacturer",
            "type_name",
            "model",
            "status",
            "last_inspection",
            "rows",
            "seats_in_row",
            "total_seats",
            "image",
        )


class AirplaneEditSerializer(serializers.ModelSerializer):

    class Meta:
        model = Airplane
        fields = (
            "id",
            "tail_number",
            "manufacturer",
            "type",
            "model",
            "status",
            "last_inspection",
            "rows",
            "seats_in_row",
            "total_seats",
        )


class AirplaneImageSerializer(serializers.ModelSerializer):

    class Meta:
        model = Airplane
        fields = (
            "id",
            "image",
        )


class CrewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Crew
        fields = (
            "id",
            "first_name",
            "last_name",
            "role",
            "license_number",
            "license_expiration",
            "is_expired",
        )


class AirportSerializer(serializers.ModelSerializer):

    class Meta:
        model = Airport
        fields = (
            "id",
            "name",
            "IATA_code",
            "ICAO_code",
            "closest_big_city",
            "timezone",
            "current_time",
            "latitude",
            "longitude",
        )


class AirportNameSerializer(serializers.ModelSerializer):

    class Meta:
        model = Airport
        fields = (
            "name",
        )


class RouteListSerializer(serializers.ModelSerializer):
    source_name = serializers.CharField(
        source="source.name",
    )
    destination_name = serializers.CharField(
        source="destination.name",
    )
    stops = AirportNameSerializer(many=True, read_only=True)

    class Meta:
        model = Route
        fields = (
            "id",
            "source_name",
            "destination_name",
            "stops",
            "distance",
        )


class RouteSerializer(serializers.ModelSerializer):

    class Meta:
        model = Route
        fields = (
            "id",
            "source",
            "destination",
            "stops",
            "distance",
        )


class RouteDetailSerializer(RouteSerializer):
    source = AirportSerializer(read_only=True)
    destination = AirportSerializer(read_only=True)
    stops = AirportSerializer(many=True, read_only=True)


class FLightListSerializer(serializers.ModelSerializer):
    airplane_model = serializers.CharField(
        source="airplane.model", read_only=True
    )
    airplane_manufacturer = serializers.CharField(
        source="airplane.manufacturer", read_only=True
    )
    crew = serializers.SerializerMethodField()
    source = serializers.CharField(
        source="route.source.IATA_code", read_only=True
    )
    destination = serializers.CharField(
        source="route.destination.IATA_code", read_only=True
    )
    stops = serializers.SerializerMethodField()

    class Meta:
        model = Flight
        fields = (
            "id",
            "airplane_model",
            "airplane_manufacturer",
            "crew",
            "source",
            "destination",
            "stops",
            "local_departure_time",
            "local_arrival_time",
            "departure_time",
            "arrival_time",
            "price",
            "status",
        )

    def get_crew(self, obj):
        return [member.full_name for member in obj.crew.all()]

    def get_stops(self, obj):
        return [airport.IATA_code for airport in obj.route.stops.all()]


class FlightSerializer(serializers.ModelSerializer):

    class Meta:
        model = Flight
        fields = (
            "id",
            "airplane",
            "crew",
            "route",
            "departure_time",
            "arrival_time",
            "local_departure_time",
            "local_arrival_time",
            "price",
            "status"
        )

    def validate_crew(self, crew):
        crew_list = list(crew)
        if len(crew_list) < 3:
            raise serializers.ValidationError(_("There should be at least 3 crew on a flight"))
        roles = [member.role for member in crew_list]

        if "PILOT" not in roles:
            raise serializers.ValidationError(_("Flight must include a PILOT"))
        if "CO-PILOT" not in roles:
            raise serializers.ValidationError(_("Flight must include a CO-PILOT"))
        if "FLIGHT_ATTENDANT" not in roles:
            raise serializers.ValidationError(_(
                "Flight must include at least one FLIGHT_ATTENDANT"
            ))
        for member in crew_list:
            if member.is_expired:
                raise serializers.ValidationError(
                    _("%(member)s has an expired license.") % {"member": str(member.full_name)}
                )
        return crew

    def validate(self, validated_data):
        crew = validated_data.get("crew")
        departure_time = validated_data.get("departure_time")
        arrival_time = validated_data.get("arrival_time")

        if departure_time >= arrival_time:
            raise serializers.ValidationError(_("Arrival time must be before departure time."))

        for member in crew:
            if not member.is_available_in(departure_time, arrival_time):
                raise serializers.ValidationError(
                    _(
                        "%(member)s is not available during this flight."
                    ) % {"member": str(member.full_name)}
                )
        return validated_data


class FlightDetailSerializer(serializers.ModelSerializer):
    airplane = AirplaneListSerializer(read_only=True)
    crew = CrewSerializer(read_only=True)
    route = RouteListSerializer(read_only=True)
    taken_seats = serializers.SerializerMethodField()

    class Meta:
        model = Flight
        fields = (
            "id",
            "airplane",
            "crew",
            "route",
            "departure_time",
            "arrival_time",
            "local_departure_time",
            "local_arrival_time",
            "price",
            "status",
            "taken_seats"
        )

    def get_taken_seats(self, obj):
        taken_seats = []
        for ticket in obj.tickets.all():
            if ticket.order.status != "CANCELLED":
                taken_seats.append(
                    {
                        "row": ticket.row,
                        "seat": ticket.seat,
                    }
                )
        return taken_seats


class TicketSerializer(serializers.ModelSerializer):

    class Meta:
        model = Ticket
        fields = (
            "id",
            "row",
            "seat",
            "flight",
            "price",
        )
        read_only_fields = ("id", "price")

    def validate(self, data):
        row = data.get("row")
        seat = data.get("seat")
        flight = data.get("flight")

        if Ticket.objects.filter(row=row, seat=seat, flight=flight).exists():
            raise serializers.ValidationError(
                {"seat": f"Seat {row}-{seat} is already taken for this flight."}
            )
        if flight.status != "PLANNED":
            raise serializers.ValidationError({"flight": _("Flight is completed or planned.")})
        return data

    def create(self, validated_data):
        flight = validated_data.get("flight")
        ticket = Ticket.objects.create(price=flight.price, **validated_data)
        return ticket


class TicketDetailSerializer(TicketSerializer):
    flight = FlightDetailSerializer(read_only=True)


class OrderCreateSerializer(serializers.ModelSerializer):
    tickets = TicketSerializer(many=True, read_only=False, allow_empty=False)

    class Meta:
        model = Order
        fields = (
            "id",
            "tickets",
        )

    def create(self, validated_data):
        tickets_data = validated_data.pop("tickets")
        user = self.context["request"].user
        seen_seats = set()

        for ticket_data in tickets_data:
            key = (ticket_data["row"], ticket_data["seat"], ticket_data["flight"].id)
            if key in seen_seats:
                raise serializers.ValidationError({
                    "tickets":
                        f"Duplicate seat {ticket_data["row"]}-{ticket_data["seat"]} "
                        f"in this order for the same flight."
                })
            seen_seats.add(key)

        with transaction.atomic():
            order = Order.objects.create(user=user, **validated_data)
            for ticket_data in tickets_data:
                flight = ticket_data.get("flight")
                price = Decimal(flight.price)
                Ticket.objects.create(order=order, price=price, **ticket_data)
            price = Decimal(order.total_price)
            if user.balance < price:
                raise serializers.ValidationError(
                    _("Not enough on balance, %(balance)s$ < %(price)s$.") % {"balance": user.balance, "price": price}
                )
            user.balance = user.balance - price
            user.save()
            return order


class OrderSerializer(serializers.ModelSerializer):
    tickets = TicketSerializer(many=True, read_only=True)

    class Meta:
        model = Order
        fields = (
            "id",
            "created_at",
            "total_price",
            "tickets",
        )


class OrderDetailSerializer(OrderSerializer):
    tickets = TicketDetailSerializer(many=True, read_only=True)


class ReturnBalanceSerializer(serializers.Serializer):
    not_returnable_tickets = TicketSerializer(many=True, read_only=True)
    returned_balance = serializers.DecimalField(max_digits=10, decimal_places=2)
    balance = serializers.DecimalField(max_digits=10, decimal_places=2)
