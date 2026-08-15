from django.core.exceptions import ValidationError
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q

from .models import Booking
from trips.models import Trip
from .forms import BookingForm
from . import services
from accounts.decorators import is_staff_or_admin, role_required


def _can_manage_booking(user, booking):
    """STAFF/ADMIN manage every booking; a PASSENGER account may only
    touch a booking whose passenger record shares their account email —
    the same rule the REST API enforces in api/permissions.py."""
    if is_staff_or_admin(user):
        return True
    return bool(user.email) and booking.passenger.email.lower() == user.email.lower()


# -------------------------------------------------
# Booking List
# -------------------------------------------------

@login_required
def booking_list(request):

    query = request.GET.get("q")

    bookings = Booking.objects.select_related(
        "passenger",
        "trip"
    ).all()

    # Passengers only ever see their own bookings; staff/admin see all.
    if not is_staff_or_admin(request.user):
        bookings = bookings.filter(passenger__email__iexact=request.user.email or "")

    if query:
        bookings = bookings.filter(
            Q(booking_reference__icontains=query)
            | Q(passenger__full_name__icontains=query)
            | Q(trip__trip_number__icontains=query)
        )

    status = request.GET.get("status")

    if status:
        bookings = bookings.filter(status=status)

    paginator = Paginator(bookings, 10)

    page = request.GET.get("page")

    bookings = paginator.get_page(page)

    return render(
        request,
        "bookings/booking_list.html",
        {
            "bookings": bookings,
            "query": query,
            "status": status,
            "status_choices": Booking.STATUS_CHOICES,
        }
    )


# -------------------------------------------------
# Create Booking
# -------------------------------------------------

@login_required
def booking_create(request):

    if request.method == "POST":

        form = BookingForm(request.POST)

        if form.is_valid():

            trip = form.cleaned_data["trip"]
            passenger = form.cleaned_data["passenger"]

            selected_seat = request.POST.get("seat_number")
            seat_number = int(selected_seat) if selected_seat else None

            try:
                booking = services.create_booking(
                    passenger=passenger,
                    trip=trip,
                    seat_number=seat_number,
                )

            except ValidationError as exc:
                messages.error(request, exc.message)
                return redirect("bookings:create")

            messages.success(request, "Booking created successfully.")

            return redirect("bookings:ticket", pk=booking.pk)

    else:
        form = BookingForm()

    return render(
        request,
        "bookings/booking_form.html",
        {"form": form}
    )


# -------------------------------------------------
# Update Booking
# -------------------------------------------------

@role_required("STAFF", "ADMIN")
def booking_update(request, pk):

    booking = get_object_or_404(Booking, pk=pk)

    old_trip = booking.trip

    if request.method == "POST":

        form = BookingForm(request.POST, instance=booking)

        if form.is_valid():

            booking = form.save(commit=False)

            new_trip = booking.trip

            if old_trip != new_trip:

                old_trip.available_seats += 1
                old_trip.save(update_fields=["available_seats"])

                if new_trip.available_seats <= 0:
                    messages.error(request, "Selected trip is full.")
                    return redirect("bookings:update", pk=pk)

                booking.seat_number = services.next_seat_number(new_trip)
                booking.amount = new_trip.route.fare

                new_trip.available_seats -= 1
                new_trip.save(update_fields=["available_seats"])

            booking.save()

            messages.success(request, "Booking updated successfully.")

            return redirect("bookings:list")

    else:
        form = BookingForm(instance=booking)

    return render(
        request,
        "bookings/booking_form.html",
        {"form": form}
    )


# -------------------------------------------------
# Delete Booking
# -------------------------------------------------

@role_required("STAFF", "ADMIN")
def booking_delete(request, pk):

    booking = get_object_or_404(Booking, pk=pk)

    if request.method == "POST":

        services.delete_booking(booking)

        messages.success(request, "Booking deleted successfully.")

        return redirect("bookings:list")

    return render(
        request,
        "bookings/booking_confirm_delete.html",
        {"booking": booking}
    )


# -------------------------------------------------
# Cancel Booking (soft — keeps the record, frees the seat)
# -------------------------------------------------

@login_required
def booking_cancel(request, pk):

    booking = get_object_or_404(Booking, pk=pk)

    if not _can_manage_booking(request.user, booking):
        messages.error(request, "You can only cancel your own bookings.")
        return redirect("bookings:list")

    if request.method == "POST":

        services.cancel_booking(booking)

        messages.success(request, "Booking cancelled and seat released.")

        return redirect("bookings:list")

    return redirect("bookings:list")


# -------------------------------------------------
# Printable Ticket
# -------------------------------------------------

@login_required
def booking_ticket(request, pk):

    booking = get_object_or_404(Booking, pk=pk)

    if not _can_manage_booking(request.user, booking):
        messages.error(request, "You can only view your own tickets.")
        return redirect("bookings:list")

    return render(
        request,
        "bookings/booking_ticket.html",
        {"booking": booking}
    )


# ---------------------------------------------
# Get Seats For Selected Trip
# ---------------------------------------------

@login_required
def available_seats(request, trip_id):

    trip = get_object_or_404(Trip, id=trip_id)

    total_seats = trip.vehicle.seating_capacity

    booked_seats = list(
        Booking.objects.filter(trip=trip).values_list("seat_number", flat=True)
    )

    return JsonResponse({
        "total_seats": total_seats,
        "booked_seats": booked_seats,
    })
