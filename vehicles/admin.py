from django.contrib import admin
from .models import Vehicle


@admin.register(Vehicle)
class VehicleAdmin(admin.ModelAdmin):

    list_display = (
        "vehicle_number",
        "vehicle_type",
        "manufacturer",
        "model",
        "year",
        "seating_capacity",
    )

    search_fields = (
        "vehicle_number",
        "manufacturer",
        "model",
    )

    list_filter = (
        "vehicle_type",
        "year",
    )

    list_per_page = 20