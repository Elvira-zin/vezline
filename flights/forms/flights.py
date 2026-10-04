from django import forms

from flights.models import Flight


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
        ]
        widgets = {
            "departure_time": forms.DateTimeInput(
                attrs={"type": "datetime-local"}
            ),
            "arrival_time": forms.DateTimeInput(
                attrs={"type": "datetime-local"}
            ),
        }
