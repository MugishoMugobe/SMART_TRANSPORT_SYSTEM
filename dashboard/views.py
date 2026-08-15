from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Sum

from accounts.decorators import is_staff_or_admin
from passengers.models import Passenger
from drivers.models import Driver
from vehicles.models import Vehicle
from routes.models import Route
from trips.models import Trip
from bookings.models import Booking


def _status_breakdown(queryset, status_choices):
    """Count-per-status plus each status's share of the total, so the
    template can size a bar directly from `pct` without doing math in
    Django template language."""

    counts = {
        row["status"]: row["count"]
        for row in queryset.values("status").annotate(count=Count("id"))
    }

    total = sum(counts.values()) or 1

    return [
        {
            "key": key,
            "label": label,
            "count": counts.get(key, 0),
            "pct": round(counts.get(key, 0) * 100 / total),
        }
        for key, label in status_choices
    ]


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


    recent_bookings_qs = Booking.objects.select_related("passenger", "trip")

    # A passenger's dashboard should only ever show their own bookings —
    # not the whole network's, which is what this looked like before.
    if not is_staff_or_admin(request.user):
        recent_bookings_qs = recent_bookings_qs.filter(
            passenger__email__iexact=request.user.email or ""
        )

    recent_bookings = recent_bookings_qs.order_by("-booking_date")[:5]


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

        "recent_bookings_label": "Recent bookings" if is_staff_or_admin(request.user) else "Your recent bookings",

        "upcoming_trips": upcoming_trips,

    }

    # Revenue detail, status breakdowns and quick actions are operational
    # controls, not passenger-facing info — same STAFF/ADMIN line the
    # reports app, and drivers/passengers modules, already draw.
    if is_staff_or_admin(request.user):
        context["show_operations_panel"] = True
        context["trip_status_breakdown"] = _status_breakdown(Trip.objects.all(), Trip.STATUS_CHOICES)
        context["booking_status_breakdown"] = _status_breakdown(Booking.objects.all(), Booking.STATUS_CHOICES)

    return render(
        request,
        "dashboard/dashboard.html",
        context
    )
