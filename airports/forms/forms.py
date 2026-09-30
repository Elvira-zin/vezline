from django import forms

from airports.models import Airport


class AirportForm(forms.ModelForm):
    class Meta:
        model = Airport
        fields = [
            "name",
            "city",
            "country",
            "code",
        ]