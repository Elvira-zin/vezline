from django.db import models
from users.models import User
from flights.models import Flight

class Booking(models.Model):
    class Status(models.TextChoices):
        CONFIRMED = "CONFIRMED", "Підтверджене"
        CANCELLED = "CANCELLED", "Скасоване"
    user = models.ForeignKey(User, on_delete=models.PROTECT, related_name="bookings",)
    flight = models.ForeignKey(Flight, on_delete=models.PROTECT, related_name="bookings",)
    booking_number = models.CharField(
        max_length=20,
        unique=True,
    )
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.CONFIRMED,
    )

    created_at = models.DateTimeField(auto_now_add=True)