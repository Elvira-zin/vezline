from django import forms

from bookings.models import Booking
from payments.models import Payment

class PaymentForm(forms.ModelForm):
    class Meta:
        model = Payment
        fields = ["payment_method", "booking"]

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["booking"].queryset = Booking.objects.filter(user=user).select_related("flight")