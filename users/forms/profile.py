from django import forms

from users.models import User


from django import forms

from users.models import User


class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ["phone"]
        labels = {
            "phone": "Phone number",
        }
        widgets = {
            "phone": forms.TextInput(
                attrs={
                    "placeholder": "Enter your phone number",
                    "inputmode": "tel",
                }
            ),
        }

    def clean_phone(self):
        phone = self.cleaned_data["phone"].strip()

        if phone and not all(
            char.isdigit() or char in "+- ()"
            for char in phone
        ):
            raise forms.ValidationError(
                "Enter a valid phone number using digits, +, -, or spaces."
            )

        digits = "".join(char for char in phone if char.isdigit())

        if phone and not 7 <= len(digits) <= 15:
            raise forms.ValidationError(
                "Phone number must contain between 7 and 15 digits."
            )

        return phone