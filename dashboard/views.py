from django.shortcuts import render
from django.contrib.auth.decorators import login_required

from passengers.models import Passenger
from drivers.models import Driver
from vehicles.models import Vehicle
from routes.models import Route
from trips.models import Trip
from bookings.models import Booking

from django.db.models import Sum


@login_required
def dashboard(request):

    total_passengers = Passenger.objects.count()

    total_drivers = Driver.objects.count()

    total_vehicles = Vehicle.objects.count()

    total_routes = Route.objects.count()

    total_trips = Trip.objects.count()

    total_bookings = Booking.objects.count()


    total_revenue = Booking.objects.filter(
        status="CONFIRMED"
    ).aggregate(
        Sum("amount")
    )["amount__sum"] or 0


    available_seats = Trip.objects.aggregate(
        Sum("available_seats")
    )["available_seats__sum"] or 0


    recent_bookings = Booking.objects.select_related(
        "passenger",
        "trip"
    ).order_by(
        "-booking_date"
    )[:5]


    upcoming_trips = Trip.objects.filter(
        status="SCHEDULED"
    ).order_by(
        "departure_time"
    )[:5]


    context = {

        "total_passengers": total_passengers,

        "total_drivers": total_drivers,

        "total_vehicles": total_vehicles,

        "total_routes": total_routes,

        "total_trips": total_trips,

        "total_bookings": total_bookings,

        "total_revenue": total_revenue,

        "available_seats": available_seats,

        "recent_bookings": recent_bookings,

        "upcoming_trips": upcoming_trips,

    }


    return render(
        request,
        "dashboard/dashboard.html",
        context
    )