from django.contrib import admin
from .models import Driver

@admin.register(Driver)
class DriverAdmin(admin.ModelAdmin):

    list_display = (
        'full_name',
        'phone',
        'license_number',
        'years_of_experience'
    )

    search_fields = (
        'full_name',
        'license_number'
    )

    ordering = (
        'full_name',
    )