from django.contrib import admin
from airport.models import (
    AirplaneType,
    Airplane,
    Crew,
    Airport,
    Route,
    Flight,
    Order,
    Ticket,
)

@admin.register(AirplaneType)
class AirplaneTypeAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "name",
    )
    search_fields = (
        "name",
    )
    readonly_fields = ("id",)

@admin.register(Airplane)
class AirplaneAdmin(admin.ModelAdmin):
    list_display = (
        "manufacturer",
        "model",
        "status",
        "last_inspection"
    )
    search_fields = (
        "manufacturer",
        "model",
        "status",
        "last_inspection",
        "tail_number",
    )
    list_filter = (
        "rows",
        "seats_in_row"
    )
    readonly_fields = ("id",)


@admin.register(Crew)
class CrewAdmin(admin.ModelAdmin):
    list_display = (
        "full_name",
        "role",
        "license_expiration"
    )
    search_fields = (
        "first_name",
        "last_name",
        "license_number",
    )
    list_filter = (
        "license_expiration",
        "role"
    )
    readonly_fields = ("id",)



@admin.register(Airport)
class AirportAdmin(admin.ModelAdmin):
    list_display = (
        "IATA_code",
        "ICAO_code",
        "closest_big_city",
        "timezone",
    )
    list_filter = (
        "timezone",
    )
    search_fields = (
        "IATA_code",
        "ICAO_code",
        "name",
        "closest_big_city",
    )
    readonly_fields = ("id",)


@admin.register(Route)
class RouteAdmin(admin.ModelAdmin):
    list_display = (
        "source",
        "destination",
        "distance"
    )
    search_fields = (
        "stops__name",
        "stops__IATA_code",
        "stops__ICAO_code",
        "source__name",
        "source__IATA_code",
        "source__ICAO_code",
        "destination__name",
        "destination__IATA_code",
        "destination__ICAO_code",
    )
    readonly_fields = ("id",)


@admin.register(Flight)
class FlightAdmin(admin.ModelAdmin):
    list_display = (
        "arrival_time",
        "departure_time",
        "route",
        "status",
        "price"
    )
    list_filter = (
        "arrival_time",
        "departure_time",
    )
    search_fields = (
        "airplane__model",
        "crew__first_name",
        "crew__last_name",
    )
    readonly_fields = ("price", "local_arrival_time", "local_departure_time", "id")


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "status",
        "created_at"
    )
    search_fields = (
        "user__first_name",
        "user__last_name",
        "user__email",
        "tickets__row",
        "tickets__seat"
    )
    readonly_fields = ("created_at", "id")


@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    list_display = (
        "row",
        "seat",
        "flight",
        "order__user"
    )
    list_filter = (
        "flight",
        "order__user"
    )
    readonly_fields = ("id", "order")