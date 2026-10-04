from django import forms

from seats.models import Seat

class SeatForm(forms.ModelForm):
    class Meta:
        model = Seat
        fields = [
            "airplane",
            "number",
            "seat_class"
        ]