from django import forms

from bookings.models import Booking
from payments.models import Payment

class PaymentForm(forms.ModelForm):
    class Meta:
        fields = ["payment_method", "booking"]
        model = Payment
        widgets = {
            # Shown as clickable cards in the template
            "payment_method": forms.RadioSelect,
        }
        error_messages = {
            "payment_method": {"required": "Choose how you want to pay."},
            "booking": {"required": "Choose a booking to pay for."},
        }

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        # Only bookings that can still be paid: the user's own, confirmed, without a payment
        self.fields["booking"].queryset = Booking.objects.filter(
            user=user,
            status=Booking.Status.CONFIRMED,
            payment__isnull=True,
        ).select_related("flight__departure_airport", "flight__arrival_airport", "seat")
        self.fields["booking"].label_from_instance = self.booking_label

        if self.instance.pk:
            self.fields.pop("booking")

    @staticmethod
    def booking_label(booking):
        flight = booking.flight
        seat = f" · seat {booking.seat.number}" if booking.seat else ""
        return (
            f"{booking.booking_number} · {flight.departure_airport.city} → "
            f"{flight.arrival_airport.city} · {flight.departure_time:%d %b}{seat}"
        )
