from django import forms

from flights.models import Flight
from airplanes.models import Airplane


class FlightForm(forms.ModelForm):
    class Meta:
        model = Flight
        fields = [
            "flight_number",
            "airplane",
            "departure_airport",
            "arrival_airport",
            "departure_time",
            "arrival_time",
            "status",
            "price",
        ]
        widgets = {
            "departure_time": forms.DateTimeInput(
                attrs={"type": "datetime-local"}
            ),
            "arrival_time": forms.DateTimeInput(
                attrs={"type": "datetime-local"}
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["airplane"].queryset = Airplane.objects.select_related("airline")
