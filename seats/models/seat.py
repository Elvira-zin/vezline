from django.db import models
from airplanes.models import Airplane

class Seat(models.Model):
    class SeatClass(models.TextChoices):
        ECONOMY = "ECONOMY", "Економ"
        BUSINESS = "BUSINESS", "Бізнес"
        FIRST = "FIRST", "Перший клас"

    airplane = models.ForeignKey(Airplane, on_delete=models.CASCADE, related_name="seats")
    number = models.CharField(max_length=10)
    seat_class = models.CharField(
        max_length=20,
        choices=SeatClass.choices,
        default=SeatClass.ECONOMY,
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["airplane", "number"], name="unique_seats_in_airplane"),
        ]

    def __str__(self):
        return f"{self.airplane} - {self.number}"