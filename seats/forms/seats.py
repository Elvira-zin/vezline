from django import forms

from airplanes.models import Airplane
from seats.models import Seat

class SeatForm(forms.ModelForm):
    class Meta:
        model = Seat
        fields = [
            "airplane",
            "number",
            "seat_class"
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["airplane"].queryset = Airplane.objects.select_related("airline")