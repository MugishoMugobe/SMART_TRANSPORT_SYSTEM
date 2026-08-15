"""
Business-rule layer for bookings.

Both the HTML views (bookings/views.py) and the REST API
(api/serializers.py) call into this module instead of duplicating seat
allocation, reference generation and overbooking rules in two places.
Every rule violation raises django.core.exceptions.ValidationError with a
human-readable message, so callers can surface it directly to a Django
form (messages.error) or wrap it into a DRF ValidationError.
"""

from django.core.exceptions import ValidationError
from django.db import transaction
from django.db.models import Max

from .models import Booking


def generate_booking_reference():
    """Next sequential reference, e.g. BK00001, BK00002, ..."""

    last_booking = Booking.objects.order_by("-id").first()

    if last_booking:
        try:
            last_number = int(last_booking.booking_reference.replace("BK", ""))
        except (TypeError, ValueError):
            last_number = last_booking.id
        new_number = last_number + 1
    else:
        new_number = 1

    return f"BK{new_number:05d}"


def next_seat_number(trip):
    """First free seat number for a trip (used when a booking is moved to
    a different trip and no seat was explicitly chosen)."""

    last = Booking.objects.filter(trip=trip).aggregate(Max("seat_number"))
    return (last["seat_number__max"] or 0) + 1


@transaction.atomic
def create_booking(passenger, trip, seat_number):
    """
    Reserve one seat on one trip for one passenger.

    Raises ValidationError on any business-rule violation:
    - the trip has no seats left
    - no seat was selected
    - the seat number is outside the vehicle's seating capacity
    - the seat is already taken on this trip
    """

    if trip.available_seats <= 0:
        raise ValidationError("No seats are available for this trip.")

    if seat_number is None:
        raise ValidationError("Please select a seat before booking.")

    if seat_number < 1 or seat_number > trip.vehicle.seating_capacity:
        raise ValidationError(
            f"Seat must be between 1 and {trip.vehicle.seating_capacity}."
        )

    if Booking.objects.filter(trip=trip, seat_number=seat_number).exists():
        raise ValidationError(
            "This seat is already booked. Please select another seat."
        )

    booking = Booking(
        passenger=passenger,
        trip=trip,
        seat_number=seat_number,
        amount=trip.route.fare,
        booking_reference=generate_booking_reference(),
    )
    booking.save()

    trip.available_seats -= 1
    trip.save(update_fields=["available_seats"])

    return booking


@transaction.atomic
def cancel_booking(booking):
    """Mark a booking cancelled and give its seat back to the trip. Safe to
    call more than once — cancelling an already-cancelled booking is a
    no-op rather than double-crediting the seat count."""

    if booking.status != "CANCELLED":
        booking.status = "CANCELLED"
        booking.save(update_fields=["status"])

        trip = booking.trip
        trip.available_seats += 1
        trip.save(update_fields=["available_seats"])

    return booking


@transaction.atomic
def delete_booking(booking):
    """Permanently remove a booking and free its seat. Distinct from
    cancel_booking(): this is the hard-delete used by staff cleanup, not
    the passenger-facing "cancel my trip" action."""

    trip = booking.trip
    trip.available_seats += 1
    trip.save(update_fields=["available_seats"])
    booking.delete()
