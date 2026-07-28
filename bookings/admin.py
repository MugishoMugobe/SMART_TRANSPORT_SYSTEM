from django.contrib import admin
from .models import Booking


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):

    list_display = (
        "booking_reference",
        "passenger",
        "trip",
        "seat_number",
        "amount",
        "payment_status",
        "status",
        "booking_date",
    )

    search_fields = (
        "booking_reference",
        "passenger__full_name",
    )

    list_filter = (
        "status",
        "payment_status",
    )

    list_per_page = 20