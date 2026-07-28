from django import forms
from .models import Booking


class BookingForm(forms.ModelForm):

    class Meta:
        model = Booking

        fields = [

            "passenger",

            "trip",

        ]

        widgets = {

            "passenger": forms.Select(
                attrs={
                    "class": "form-control"
                }
            ),

            "trip": forms.Select(
                attrs={
                    "class": "form-control",
                    "id": "trip-select"
                }
            ),

        }