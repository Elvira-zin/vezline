from django import forms

from airplanes.models import Airplane


class AirplaneForm(forms.ModelForm):
    economy_seats = forms.IntegerField(
        min_value=0,
        initial=0,
        label="Economy seats",
    )
    business_seats = forms.IntegerField(
        min_value=0,
        initial=0,
        label="Business seats",
    )
    first_class_seats = forms.IntegerField(
        min_value=0,
        initial=0,
        label="First class seats",
    )

    class Meta:
        model = Airplane
        fields = [
            "airline",
            "model",
            "registration_number",
            "capacity",
        ]

    def clean(self):
        cleaned_data = super().clean()

        capacity = cleaned_data.get("capacity")
        economy = cleaned_data.get("economy_seats")
        business = cleaned_data.get("business_seats")
        first_class = cleaned_data.get("first_class_seats")

        if None not in (capacity, economy, business, first_class):
            total_seats = economy + business + first_class

            if total_seats != capacity:
                raise forms.ValidationError(
                    f"The total number of seats ({total_seats}) "
                    f"must equal the airplane capacity ({capacity})."
                )

        return cleaned_data