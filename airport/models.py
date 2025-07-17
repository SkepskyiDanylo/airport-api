import uuid

from django.core.validators import MinValueValidator
from django.db import models


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
    name = models.CharField(max_length=255)
    type = models.ForeignKey(AirplaneType, on_delete=models.CASCADE, related_name="airplanes")
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
        return self.name

    @property
    def total_seats(self):
        return self.rows * self.seats_in_row


class Crew(BaseModel):
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


class Airport(BaseModel):
    name = models.CharField(max_length=255)
    closest_big_city = models.CharField(max_length=255)


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
