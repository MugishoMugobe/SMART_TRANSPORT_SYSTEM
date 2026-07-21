from django.contrib import admin
from .models import Booking

@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):

    list_display = (
        'passenger',
        'trip',
        'seat_number',
        'amount',
        'is_paid',
        'booking_date'
    )

    search_fields = (
        'passenger__full_name',
    )

    list_filter = (
        'is_paid',
        'booking_date'
    )