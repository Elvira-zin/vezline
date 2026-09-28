from django import forms

from airlines.models import Airline


class AirlineForm(forms.ModelForm):
    class Meta:
        model = Airline
        fields = [
            "name",
            "website",
            "logo",
            "description",
            "phone",
            "email",
            "code",
            "country",
        ]