from django.contrib import admin
from .models import Route

@admin.register(Route)
class RouteAdmin(admin.ModelAdmin):

    list_display = (
        'origin',
        'destination',
        'distance',
        'estimated_duration'
    )

    search_fields = (
        'origin',
        'destination'
    )