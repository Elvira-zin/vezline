from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models
from airports.models import Airport
from airplanes.models import Airplane

class Flight(models.Model):
    class Status(models.TextChoices):
        SCHEDULED = "SCHEDULED", "Запланований"
        CANCELLED = "CANCELLED", "Скасований"
        COMPLETED = "COMPLETED", "Завершений"

    airplane = models.ForeignKey(
        Airplane,
        on_delete=models.PROTECT,
        related_name="flights",
    )

    departure_airport = models.ForeignKey(
        Airport,
        on_delete=models.PROTECT,
        related_name="departures",
    )

    arrival_airport = models.ForeignKey(
        Airport,
        on_delete=models.PROTECT,
        related_name="arrivals",
    )

    flight_number = models.CharField(
        max_length=10,
        unique=True,
    )

    departure_time = models.DateTimeField()

    arrival_time = models.DateTimeField()

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.SCHEDULED,
    )

    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)],
    )

    def __str__(self):
        return self.flight_number

    def clean(self):
        errors = {}

        if self.departure_airport_id and self.departure_airport_id == self.arrival_airport_id:
            errors["arrival_airport"] = "Arrival airport must be different from departure airport."

        if self.departure_time is not None and self.arrival_time is not None:
            if self.departure_time >= self.arrival_time:
                errors["arrival_time"] = "Arrival time must be later than departure time."

        if errors:
            raise ValidationError(errors)


