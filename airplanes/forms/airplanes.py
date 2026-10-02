from django import forms

from airplanes.models import Airplane

class AirplaneForm(forms.ModelForm):
    class Meta:
        model = Airplane
        fields = [
            "airline",
            "model",
            "registration_number",
        ]
