from django import forms

from bookings.models import Booking
from flights.models import Flight
from seats.models import Seat


class BookingForm(forms.ModelForm):
    class Meta:
        model = Booking
        fields = ["flight", "seat"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["seat"].queryset = Seat.objects.none()

        flight_id = (
            self.data.get("flight")
            or self.initial.get("flight")
            or getattr(self.instance, "flight_id", None)
        )

        if flight_id:
            self.fields["seat"].queryset = Seat.objects.filter(
                airplane__flights__id=flight_id
            )