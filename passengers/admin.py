from django.contrib import admin
from .models import Passenger


@admin.register(Passenger)
class PassengerAdmin(admin.ModelAdmin):

    list_display = (
        "id",
        "full_name",
        "email",
        "phone",
    )

    search_fields = (
        "full_name",
        "email",
        "phone",
    )

    list_per_page = 20