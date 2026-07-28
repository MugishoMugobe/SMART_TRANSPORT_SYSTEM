from django import forms
from .models import Vehicle


class VehicleForm(forms.ModelForm):
    class Meta:
        model = Vehicle
        fields = [
            "vehicle_number",
            "vehicle_type",
            "seating_capacity",
            "manufacturer",
            "model",
            "year",
            "image",
        ]

        widgets = {
            "vehicle_number": forms.TextInput(attrs={"class": "form-control"}),
            "vehicle_type": forms.Select(attrs={"class": "form-select"}),
            "seating_capacity": forms.NumberInput(attrs={"class": "form-control"}),
            "manufacturer": forms.TextInput(attrs={"class": "form-control"}),
            "model": forms.TextInput(attrs={"class": "form-control"}),
            "year": forms.NumberInput(attrs={"class": "form-control"}),
        }