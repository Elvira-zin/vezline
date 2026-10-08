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

        numbers = self.seats.values_list("number", flat=True)
        max_number = max((int(n) for n in numbers if n.isdigit()), default=0)

        if self.capacity < max_number:
            raise ValidationError({
                "capacity": f"Capacity cannot be lower than {max_number}: "
                            f"this airplane already has a seat with that number. "
                            f"Delete seats above the new capacity first."
            })