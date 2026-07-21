from django.contrib import admin
from .models import Vehicle

@admin.register(Vehicle)
class VehicleAdmin(admin.ModelAdmin):

    list_display = (
        'vehicle_number',
        'vehicle_type',
        'seating_capacity',
        'manufacturer',
        'year'
    )

    search_fields = (
        'vehicle_number',
        'manufacturer'
    )

    list_filter = (
        'vehicle_type',
        'year'
    )