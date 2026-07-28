from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q, Max

from .models import Booking
from trips.models import Trip
from .forms import BookingForm



# -------------------------------------------------
# Generate Booking Reference
# Example: BK00001
# -------------------------------------------------

def generate_booking_reference():

    last_booking = Booking.objects.order_by("-id").first()

    if last_booking:

        try:
            last_number = int(
                last_booking.booking_reference.replace("BK", "")
            )

        except Exception:

            last_number = last_booking.id


        new_number = last_number + 1

    else:

        new_number = 1


    return f"BK{new_number:05d}"



# -------------------------------------------------
# Get Next Seat Number (backup function)
# -------------------------------------------------

def next_seat_number(trip):

    last = Booking.objects.filter(
        trip=trip
    ).aggregate(
        Max("seat_number")
    )


    if last["seat_number__max"]:

        return last["seat_number__max"] + 1


    return 1



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


    if query:

        bookings = bookings.filter(

            Q(booking_reference__icontains=query)
            |
            Q(passenger__full_name__icontains=query)
            |
            Q(trip__trip_number__icontains=query)

        )


    paginator = Paginator(
        bookings,
        10
    )


    page = request.GET.get("page")


    bookings = paginator.get_page(page)


    return render(

        request,

        "bookings/booking_list.html",

        {

            "bookings": bookings,

            "query": query

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


            booking = form.save(
                commit=False
            )


            trip = booking.trip



            # Prevent overbooking

            if trip.available_seats <= 0:


                messages.error(

                    request,

                    "No seats are available for this trip."

                )


                return redirect(
                    "bookings:create"
                )



            # Get selected seat

            selected_seat = request.POST.get(
                "seat_number"
            )


            if not selected_seat:


                messages.error(

                    request,

                    "Please select a seat before booking."

                )


                return redirect(
                    "bookings:create"
                )



            booking.seat_number = int(
                selected_seat
            )



            # Prevent duplicate seat booking

            seat_exists = Booking.objects.filter(

                trip=trip,

                seat_number=booking.seat_number

            ).exists()



            if seat_exists:


                messages.error(

                    request,

                    "This seat is already booked. Please select another seat."

                )


                return redirect(
                    "bookings:create"
                )



            # Generate booking reference

            booking.booking_reference = generate_booking_reference()



            # Calculate fare

            booking.amount = trip.route.fare



            booking.save()



            # Reduce available seats

            trip.available_seats -= 1

            trip.save()



            messages.success(

                request,

                "Booking created successfully."

            )



            return redirect(

                "bookings:ticket",

                pk=booking.pk

            )



    else:


        form = BookingForm()



    return render(

        request,

        "bookings/booking_form.html",

        {

            "form": form

        }

    )



# -------------------------------------------------
# Update Booking
# -------------------------------------------------

@login_required
def booking_update(request, pk):


    booking = get_object_or_404(

        Booking,

        pk=pk

    )


    old_trip = booking.trip



    if request.method == "POST":


        form = BookingForm(

            request.POST,

            instance=booking

        )


        if form.is_valid():


            booking = form.save(
                commit=False
            )


            new_trip = booking.trip



            if old_trip != new_trip:


                old_trip.available_seats += 1

                old_trip.save()



                if new_trip.available_seats <= 0:


                    messages.error(

                        request,

                        "Selected trip is full."

                    )


                    return redirect(

                        "bookings:update",

                        pk=pk

                    )



                booking.seat_number = next_seat_number(
                    new_trip
                )


                booking.amount = new_trip.route.fare



                new_trip.available_seats -= 1

                new_trip.save()



            booking.save()



            messages.success(

                request,

                "Booking updated successfully."

            )


            return redirect(

                "bookings:list"

            )



    else:


        form = BookingForm(
            instance=booking
        )



    return render(

        request,

        "bookings/booking_form.html",

        {

            "form": form

        }

    )



# -------------------------------------------------
# Delete Booking
# -------------------------------------------------

@login_required
def booking_delete(request, pk):


    booking = get_object_or_404(

        Booking,

        pk=pk

    )



    if request.method == "POST":


        trip = booking.trip



        trip.available_seats += 1

        trip.save()



        booking.delete()



        messages.success(

            request,

            "Booking deleted successfully."

        )



        return redirect(

            "bookings:list"

        )



    return render(

        request,

        "bookings/booking_confirm_delete.html",

        {

            "booking": booking

        }

    )



# -------------------------------------------------
# Printable Ticket
# -------------------------------------------------

@login_required
def booking_ticket(request, pk):


    booking = get_object_or_404(

        Booking,

        pk=pk

    )


    return render(

        request,

        "bookings/booking_ticket.html",

        {

            "booking": booking

        }

    )

# ---------------------------------------------
# Get Seats For Selected Trip
# ---------------------------------------------

@login_required
def available_seats(request, trip_id):

    trip = get_object_or_404(
        Trip,
        id=trip_id
    )


    # Vehicle capacity

    total_seats = trip.vehicle.seating_capacity


    # Seats already booked

    booked_seats = list(

        Booking.objects.filter(

            trip=trip

        ).values_list(

            "seat_number",

            flat=True

        )

    )


    return JsonResponse(

        {

            "total_seats": total_seats,

            "booked_seats": booked_seats

        }

    )