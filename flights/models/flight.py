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

    def __str__(self):
        return self.flight_number


