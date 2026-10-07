from django.db import models
from django.core.validators import MinValueValidator
from airlines.models import Airline

class Airplane(models.Model):
    airline = models.ForeignKey(Airline, on_delete=models.CASCADE, related_name="airplanes",)
    model = models.CharField(max_length=100)
    registration_number = models.CharField(max_length=20, unique=True)
    capacity = models.PositiveIntegerField(validators=[MinValueValidator(1)])

    def __str__(self):
        return f"{self.airline.name} - {self.model} ({self.registration_number})"

