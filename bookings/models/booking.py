from django.db import models

from seats.models import Seat
from users.models import User
from flights.models import Flight
from django.core.exceptions import ValidationError
from django.db.models import Q

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
    seat = models.ForeignKey(
        Seat,
        on_delete=models.PROTECT,
        related_name="bookings",
        null=True,
        blank=True,
    )
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.CONFIRMED,
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.flight.flight_number} - {self.booking_number}"
      
    def clean(self):
        if not self.flight_id or not self.seat_id:
            return

        if self.seat.airplane_id != self.flight.airplane_id:
            raise ValidationError({
                "seat": "This seat does not belong to the airplane for this flight."
            })

        existing_booking = Booking.objects.filter(
            flight=self.flight,
            seat=self.seat,
            status=self.Status.CONFIRMED,
        ).exclude(pk=self.pk)

        if existing_booking.exists():
            raise ValidationError({
                "seat": "This seat is already booked for this flight."
            })
