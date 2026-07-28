from django.contrib import admin
from .models import Route


@admin.register(Route)
class RouteAdmin(admin.ModelAdmin):

    list_display = (
        "origin",
        "destination",
        "distance",
        "fare",
        "status",
    )

    search_fields = (
        "origin",
        "destination",
    )

    list_filter = (
        "status",
    )

    list_per_page = 20