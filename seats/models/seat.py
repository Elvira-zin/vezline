from django.core.exceptions import ValidationError
from django.db import models
from airplanes.models import Airplane

class Seat(models.Model):
    class SeatClass(models.TextChoices):
        ECONOMY = "ECONOMY", "Економ"
        BUSINESS = "BUSINESS", "Бізнес"
        FIRST = "FIRST", "Перший клас"

    airplane = models.ForeignKey(Airplane, on_delete=models.CASCADE, related_name="seats")
    # Kept as CharField on purpose: v1 accepts digits only (see clean()),
    # but this leaves room for row+letter seat codes like "12A" later.
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

    def clean(self):
        if not self.number:
            return
        if not self.number.isdigit():
            raise ValidationError({"number": "Number must contain only digits."})
        if not self.airplane_id:
            return
        number = int(self.number)
        if number < 1 or number > self.airplane.capacity:
            raise ValidationError({"number": f"Available seat numbers are between 1 and {self.airplane.capacity}."})
