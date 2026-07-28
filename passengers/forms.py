from django import forms
from .models import Passenger


class PassengerForm(forms.ModelForm):
    class Meta:
        model = Passenger
        fields = [
            "full_name",
            "email",
            "phone",
            "address",
            "national_id",
        ]

        widgets = {
            "full_name": forms.TextInput(attrs={
                "class": "form-control"
            }),
            "email": forms.EmailInput(attrs={
                "class": "form-control"
            }),
            "phone": forms.TextInput(attrs={
                "class": "form-control"
            }),
            "address": forms.Textarea(attrs={
                "class": "form-control",
                "rows": 3
            }),
            "national_id": forms.TextInput(attrs={
                "class": "form-control"
            }),
        }