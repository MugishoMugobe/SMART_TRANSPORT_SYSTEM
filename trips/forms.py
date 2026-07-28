from django import forms
from .models import Trip


class TripForm(forms.ModelForm):

    class Meta:

        model = Trip

        fields = [

            "trip_number",
            "vehicle",
            "driver",
            "route",
            "departure_time",
            "arrival_time",
            "available_seats",
            "status",
            "notes",

        ]

        widgets = {

            "trip_number": forms.TextInput(
                attrs={"class":"form-control"}
            ),

            "vehicle": forms.Select(
                attrs={"class":"form-select"}
            ),

            "driver": forms.Select(
                attrs={"class":"form-select"}
            ),

            "route": forms.Select(
                attrs={"class":"form-select"}
            ),

            "departure_time": forms.DateTimeInput(
                attrs={
                    "class":"form-control",
                    "type":"datetime-local"
                }
            ),

            "arrival_time": forms.DateTimeInput(
                attrs={
                    "class":"form-control",
                    "type":"datetime-local"
                }
            ),

            "available_seats": forms.NumberInput(
                attrs={"class":"form-control"}
            ),

            "status": forms.Select(
                attrs={"class":"form-select"}
            ),

            "notes": forms.Textarea(
                attrs={
                    "class":"form-control",
                    "rows":3
                }
            ),
        }