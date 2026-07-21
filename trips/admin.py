from django.contrib import admin
from .models import Trip

@admin.register(Trip)
class TripAdmin(admin.ModelAdmin):

    list_display = (
        'route',
        'vehicle',
        'driver',
        'departure_time',
        'arrival_time',
        'status'
    )

    search_fields = (
        'route__origin',
        'route__destination',
        'vehicle__vehicle_number',
        'driver__full_name'
    )

    list_filter = (
        'status',
        'departure_time'
    )