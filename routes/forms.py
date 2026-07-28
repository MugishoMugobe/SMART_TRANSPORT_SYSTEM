from django import forms
from .models import Route


class RouteForm(forms.ModelForm):

    class Meta:
        model = Route

        fields = [
            "origin",
            "destination",
            "distance",
            "estimated_duration",
            "fare",
            "status",
            "description",
        ]

        widgets = {

            "origin": forms.TextInput(
                attrs={"class":"form-control"}
            ),

            "destination": forms.TextInput(
                attrs={"class":"form-control"}
            ),

            "distance": forms.NumberInput(
                attrs={"class":"form-control"}
            ),

            "estimated_duration": forms.TimeInput(
                attrs={
                    "class":"form-control",
                    "type":"time"
                }
            ),

            "fare": forms.NumberInput(
                attrs={"class":"form-control"}
            ),

            "status": forms.Select(
                attrs={"class":"form-select"}
            ),

            "description": forms.Textarea(
                attrs={
                    "class":"form-control",
                    "rows":3
                }
            ),
        }