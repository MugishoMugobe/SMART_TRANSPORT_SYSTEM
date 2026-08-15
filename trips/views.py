from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q

from .models import Trip
from .forms import TripForm
from accounts.decorators import role_required


@login_required
def trip_list(request):

    query = request.GET.get("q")

    trips = Trip.objects.select_related(
        "vehicle",
        "driver",
        "route"
    ).all().order_by("-departure_time")

    if query:
        trips = trips.filter(
            Q(trip_number__icontains=query) |
            Q(vehicle__vehicle_number__icontains=query) |
            Q(driver__full_name__icontains=query) |
            Q(route__origin__icontains=query) |
            Q(route__destination__icontains=query)
        )

    status = request.GET.get("status")

    if status:
        trips = trips.filter(status=status)

    paginator = Paginator(trips, 10)

    page = request.GET.get("page")

    trips = paginator.get_page(page)

    return render(
        request,
        "trips/trip_list.html",
        {
            "trips": trips,
            "query": query,
            "status": status,
            "status_choices": Trip.STATUS_CHOICES,
        }
    )


@role_required("STAFF", "ADMIN")
def trip_create(request):

    if request.method == "POST":

        form = TripForm(request.POST)

        if form.is_valid():

            trip = form.save(commit=False)

            trip.available_seats = trip.vehicle.seating_capacity

            trip.save()

            messages.success(
                request,
                "Trip created successfully."
            )

            return redirect("trips:list")

    else:

        form = TripForm()

    return render(
        request,
        "trips/trip_form.html",
        {
            "form": form
        }
    )


@role_required("STAFF", "ADMIN")
def trip_update(request, pk):

    trip = get_object_or_404(
        Trip,
        pk=pk
    )

    if request.method == "POST":

        form = TripForm(
            request.POST,
            instance=trip
        )

        if form.is_valid():

            form.save()

            messages.success(
                request,
                "Trip updated successfully."
            )

            return redirect("trips:list")

    else:

        form = TripForm(instance=trip)

    return render(
        request,
        "trips/trip_form.html",
        {
            "form": form
        }
    )


@role_required("STAFF", "ADMIN")
def trip_delete(request, pk):

    trip = get_object_or_404(
        Trip,
        pk=pk
    )

    if request.method == "POST":

        trip.delete()

        messages.success(
            request,
            "Trip deleted successfully."
        )

        return redirect("trips:list")

    return render(
        request,
        "trips/trip_confirm_delete.html",
        {
            "trip": trip
        }
    )