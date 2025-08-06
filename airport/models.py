import os
import uuid
from datetime import datetime, timedelta
from decimal import Decimal
from math import radians, cos, sin, asin, sqrt
import pytz
from django.core.validators import MinValueValidator
from django.db import models
from django.utils.timezone import now, localtime
from django.utils.translation import gettext_lazy as _


class BaseModel(models.Model):
    """Base model for all models."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    class Meta:
        abstract = True


class AirplaneType(BaseModel):
    name = models.CharField(max_length=255)

    class Meta:
        verbose_name_plural = _("Airplane Types")
        verbose_name = _("Airplane Type")

    def __str__(self):
        return self.name


def airplane_image(instance: "Airplane", filename: str) -> str:
    ext = filename.split(".")[-1].lower()
    name = f"{instance.manufacturer}-{instance.model}-{uuid.uuid4()}.{ext}"
    return os.path.join("airplanes", name)


class Airplane(BaseModel):
    MANUFACTURER_CHOICES = (
        ("AIRBUS", _("Airbus")),
        ("BOEING", _("Boeing")),
        ("EMBRAER", _("Embraer")),
        ("BOMBARDIER", _("Bombardier")),
        ("ATR", _("ATR")),
        ("SUKHOI", _("Sukhoi")),
        ("COMAC", _("COMAC")),
        ("MCDONNELL_DOUGLAS", _("McDonnell Douglas")),
        ("LOCKHEED", _("Lockheed")),
        ("IL", _("Ilyushin")),
        ("TU", _("Tupolev")),
        ("ANTONOV", _("Antonov")),
    )
    STATUS_CHOICES = (
        ("ACTIVE", _("Active")),
        ("INACTIVE", _("Inactive")),
        ("FROZEN", _("Frozen")),
    )
    type = models.ForeignKey(AirplaneType, on_delete=models.CASCADE, related_name="airplanes")
    tail_number = models.CharField(max_length=255, unique=True)
    manufacturer = models.CharField(max_length=30, choices=MANUFACTURER_CHOICES)
    model = models.CharField(max_length=100)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="ACTIVE")
    last_inspection = models.DateTimeField(null=True, blank=True)
    rows = models.IntegerField(
        validators=[
            MinValueValidator(1),
        ]
    )
    seats_in_row = models.IntegerField(
        validators=[
            MinValueValidator(1),
        ]
    )
    image = models.ImageField(upload_to=airplane_image, null=True, blank=True)

    class Meta:
        verbose_name_plural = _("Airplanes")
        verbose_name = _("Airplane")

    def __str__(self) -> str:
        return f"{self.manufacturer} {self.model}: {self.tail_number}"

    @property
    def total_seats(self) -> int:
        return self.rows * self.seats_in_row


class Crew(BaseModel):
    ROLE_CHOICES = (
        ("PILOT", _("Pilot"),),
        ("CO-PILOT", _("Co-pilot"),),
        ("FLIGHT_ATTENDANT", _("Flight Attendant"),),
        ("ENGINEER", _("Engineer"),),
    )

    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    role = models.CharField(max_length=100, choices=ROLE_CHOICES)
    license_number = models.CharField(max_length=32, unique=True)
    license_expiration = models.DateTimeField()

    class Meta:
        verbose_name_plural = _("Crew")
        verbose_name = _("Crew")

    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}"

    @property
    def is_expired(self) -> bool:
        if now() < self.license_expiration:
            return False
        return True

    def is_available_in(self, start_time, end_time) -> bool:
        return not self.flights.filter(
            departure_time__lt=end_time,
            arrival_time__gt=start_time
        ).exists()

    def __str__(self):
        return f"{self.role}: {self.first_name} {self.last_name}"


class Airport(BaseModel):
    name = models.CharField(max_length=255)
    IATA_code = models.CharField(max_length=3, unique=True)
    ICAO_code = models.CharField(max_length=4, unique=True)
    closest_big_city = models.CharField(max_length=255)
    timezone = models.CharField(
        max_length=50,
        choices=[(tz, tz) for tz in pytz.common_timezones],
        default="UTC"
    )
    latitude = models.DecimalField(
        max_digits=9, decimal_places=6,
    )
    longitude = models.DecimalField(
        max_digits=9, decimal_places=6,
    )

    @property
    def current_time(self) -> datetime:
        tz = pytz.timezone(self.timezone)
        return localtime(now(), timezone=tz).isoformat()

    class Meta:
        verbose_name_plural = _("Airports")
        verbose_name = _("Airport")

    def __str__(self):
        return f"{self.IATA_code} - {self.ICAO_code} - {self.name}"


class Route(BaseModel):
    source = models.ForeignKey(Airport, on_delete=models.CASCADE, related_name="departures")
    destination = models.ForeignKey(Airport, on_delete=models.CASCADE, related_name="arrivals")
    stops = models.ManyToManyField(Airport, related_name="stops", blank=True)
    distance = models.IntegerField(help_text=_("Distance in kilometers"))

    def haversine_distance(self, lat1, lon1, lat2, lon2):
        """
        Calculate the great-circle distance between two points
        on the Earth using the Haversine formula.
        """
        lat1, lon1, lat2, lon2 = map(float, (lat1, lon1, lat2, lon2))
        lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])

        dlon = lon2 - lon1
        dlat = lat2 - lat1
        a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
        c = 2 * asin(sqrt(a))
        r = 6371  # Radius of Earth in kilometers
        return round(c * r)

    def save(self, *args, **kwargs):
        if self.source and self.destination:
            self.distance = self.haversine_distance(
                self.source.latitude,
                self.source.longitude,
                self.destination.latitude,
                self.destination.longitude
            )
        super().save(*args, **kwargs)

    class Meta:
        verbose_name_plural = _("Routes")
        verbose_name = _("Route")

    def __str__(self):
        return f"{self.source} -> {self.destination}"


class Flight(BaseModel):
    airplane = models.ForeignKey(Airplane, on_delete=models.CASCADE)
    crew = models.ManyToManyField(Crew, blank=True, related_name="flights")
    route = models.ForeignKey(Route, on_delete=models.CASCADE, related_name="flights")
    departure_time = models.DateTimeField()
    arrival_time = models.DateTimeField()

    class Meta:
        ordering = ("departure_time", "arrival_time")
        verbose_name_plural = _("Flights")
        verbose_name = _("Flight")

    @property
    def status(self) -> str:
        time_now = now()
        if self.departure_time > time_now:
            return "PLANNED"
        elif self.arrival_time < time_now:
            return "COMPLETED"
        return "IN_PROGRESS"

    @property
    def price(self) -> float:
        if not self.arrival_time or now() > self.arrival_time:
            return 0.0
        base_price = self.route.distance * 0.025

        if self.departure_time - now() < timedelta(days=3):
            base_price *= 1.2

        total_seats = self.airplane.total_seats
        booked_seats = self.tickets.count()

        if total_seats:
            occupancy = booked_seats / total_seats
            if occupancy > 0.8:
                base_price *= 1.3

        return round(base_price, 2)

    @property
    def local_departure_time(self) -> datetime:
        tz = pytz.timezone(self.route.source.timezone)
        return localtime(self.departure_time, timezone=tz).isoformat()

    @property
    def local_arrival_time(self) -> datetime:
        tz = pytz.timezone(self.route.destination.timezone)
        return localtime(self.arrival_time, timezone=tz).isoformat()

    def __str__(self):
        return f"{self.arrival_time}:{self.departure_time}"


class Order(BaseModel):
    STATUS_CHOICES = (
        ("CANCELLED", _("Cancelled")),
        ("PAID", _("Paid")),
    )
    created_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey("user.User", on_delete=models.CASCADE)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="PAID")

    class Meta:
        verbose_name_plural = _("Orders")
        verbose_name = _("Order")

    @property
    def total_price(self):
        price = Decimal(0)
        tickets = self.tickets.all()
        for ticket in tickets:
            price += ticket.price
        return price

    def __str__(self):
        return f"{self.user} | {self.created_at}"


class Ticket(BaseModel):
    row = models.IntegerField(
        validators=[
            MinValueValidator(1),
        ]
    )
    seat = models.IntegerField(
        validators=[
            MinValueValidator(1),
        ]
    )
    price = models.DecimalField(max_digits=10, decimal_places=2)
    flight = models.ForeignKey(Flight, on_delete=models.CASCADE, related_name="tickets")
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="tickets")

    class Meta:
        verbose_name_plural = _("Tickets")
        verbose_name = _("Ticket")
        constraints = [
            models.UniqueConstraint(
                fields=["row", "seat", "flight"], name="unique_ticket_seat_and_flight"
            )
        ]

    def __str__(self):
        return f"{self.row}:{self.seat}"
