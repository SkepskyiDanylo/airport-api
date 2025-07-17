import uuid

import pytz
from django.core.validators import MinValueValidator
from django.db import models
from django.db.models import TextChoices
from django.utils.translation import gettext as _


class BaseModel(models.Model):
    """Base model for all models."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    class Meta:
        abstract = True


class AirplaneType(BaseModel):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


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

    def __str__(self):
        return f"{self.manufacturer} {self.model}: {self.tail_number}"

    @property
    def total_seats(self):
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

    def __str__(self):
        return f"{self.IATA_code} - {self.ICAO_code} - {self.name}"


class Route(BaseModel):
    source = models.ForeignKey(Airport, on_delete=models.CASCADE, related_name="departures")
    destination = models.ForeignKey(Airport, on_delete=models.CASCADE, related_name="arrivals")
    distance = models.IntegerField()

    def __str__(self):
        return f"{self.source} -> {self.destination}"


class Flight(BaseModel):
    airplane = models.ForeignKey(Airplane, on_delete=models.CASCADE)
    crew = models.ManyToManyField(Crew, blank=True, related_name="flights")
    route = models.ForeignKey(Route, on_delete=models.CASCADE, related_name="flights")
    departure_time = models.DateTimeField()
    arrival_time = models.DateTimeField()


class Order(BaseModel):
    created_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey("user.User", on_delete=models.CASCADE)


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
    flight = models.ForeignKey(Flight, on_delete=models.CASCADE, related_name="tickets")
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="tickets")
