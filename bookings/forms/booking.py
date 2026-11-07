from django import forms

from bookings.models import Booking
from seats.models import Seat


class BookingForm(forms.ModelForm):
    class Meta:
        model = Booking
        fields = ["flight", "seat"]
        widgets = {
            # The template draws a seat map with radio buttons named "seat"
            "flight": forms.HiddenInput,
            "seat": forms.RadioSelect,
        }
        error_messages = {
            "seat": {"required": "Pick a seat on the map."},
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["seat"].required = True
        self.fields["seat"].queryset = Seat.objects.none()

        flight_id = (
            self.data.get("flight")
            or self.initial.get("flight")
            or getattr(self.instance, "flight_id", None)
        )

        if str(flight_id or "").isdigit():
            self.fields["seat"].queryset = Seat.objects.filter(
                airplane__flights__id=flight_id
            )
