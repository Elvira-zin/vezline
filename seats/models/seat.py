import math
import re

from django.core.exceptions import ValidationError
from django.db import models
from airplanes.models import Airplane

# Seat numbers are a row number + a letter, like "12C" (see sync_airplane_seats)
SEAT_NUMBER = re.compile(r"^(?P<row>\d+)(?P<letter>[A-F])$")
SEATS_PER_ROW = 6

class Seat(models.Model):
    class SeatClass(models.TextChoices):
        ECONOMY = "ECONOMY", "Економ"
        BUSINESS = "BUSINESS", "Бізнес"
        FIRST = "FIRST", "Перший клас"

    airplane = models.ForeignKey(Airplane, on_delete=models.CASCADE, related_name="seats")
    # Row number + letter, e.g. "12C" (checked in clean())
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

        self.number = self.number.strip().upper()
        match = SEAT_NUMBER.match(self.number)
        if not match:
            raise ValidationError({"number": "Use a row number and a letter A–F, e.g. 12C."})

        if not self.airplane_id:
            return

        row = int(match["row"])
        last_row = math.ceil(self.airplane.capacity / SEATS_PER_ROW)
        if row < 1 or row > last_row:
            raise ValidationError({"number": f"This airplane has rows 1–{last_row}."})
