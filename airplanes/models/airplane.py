from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models
from airlines.models import Airline

class Airplane(models.Model):
    airline = models.ForeignKey(Airline, on_delete=models.CASCADE, related_name="airplanes",)
    model = models.CharField(max_length=100)
    registration_number = models.CharField(max_length=20, unique=True)
    capacity = models.PositiveIntegerField(validators=[MinValueValidator(1)])

    def __str__(self):
        return f"{self.airline.name} - {self.model} ({self.registration_number})"

    def clean(self):
        if self.pk is None:
            return
        if self.capacity is None:
            return

        # Seat numbers are like "12C", so compare with how many seats exist
        seats_count = self.seats.count()

        if self.capacity < seats_count:
            raise ValidationError({
                "capacity": f"Capacity cannot be lower than {seats_count}: "
                            f"this airplane already has {seats_count} seats. "
                            f"Delete some seats first."
            })