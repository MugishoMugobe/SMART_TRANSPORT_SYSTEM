from django import forms
from .models import Driver

class DriverForm(forms.ModelForm):
    class Meta:
        model = Driver
        fields = [
            "full_name",
            "phone",
            "license_number",
            "years_of_experience",
            "photo",
        ]

        widgets = {
            "full_name": forms.TextInput(attrs={"class": "form-control"}),
            "phone": forms.TextInput(attrs={"class": "form-control"}),
            "license_number": forms.TextInput(attrs={"class": "form-control"}),
            "years_of_experience": forms.NumberInput(attrs={"class": "form-control"}),
        }