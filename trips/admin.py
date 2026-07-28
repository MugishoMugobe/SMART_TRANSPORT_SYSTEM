from django.contrib import admin
from .models import Trip


@admin.register(Trip)
class TripAdmin(admin.ModelAdmin):

    list_display = (
        "trip_number",
        "vehicle",
        "driver",
        "route",
        "departure_time",
        "arrival_time",
        "available_seats",
        "status",
    )

    search_fields = (
        "trip_number",
        "vehicle__vehicle_number",
        "driver__full_name",
    )

    list_filter = (
        "status",
    )

    list_per_page = 20