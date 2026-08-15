from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator

from .models import Vehicle
from .forms import VehicleForm
from accounts.decorators import role_required


# Reading the fleet list is fine for any authenticated role — only
# managing it (create/update/delete) is staff/admin only.

@login_required
def vehicle_list(request):

    query = request.GET.get("q")

    vehicles = Vehicle.objects.all()

    if query:
        vehicles = vehicles.filter(
            vehicle_number__icontains=query
        )

    vehicle_type = request.GET.get("vehicle_type")

    if vehicle_type:
        vehicles = vehicles.filter(vehicle_type=vehicle_type)

    paginator = Paginator(vehicles, 10)

    page = request.GET.get("page")

    vehicles = paginator.get_page(page)

    return render(
        request,
        "vehicles/vehicle_list.html",
        {
            "vehicles": vehicles,
            "query": query,
            "vehicle_type": vehicle_type,
            "vehicle_types": Vehicle.VEHICLE_TYPES,
        }
    )


@role_required("STAFF", "ADMIN")
def vehicle_create(request):

    if request.method == "POST":

        form = VehicleForm(
            request.POST,
            request.FILES
        )

        if form.is_valid():
            form.save()
            messages.success(request, "Vehicle added successfully.")
            return redirect("vehicles:list")

    else:
        form = VehicleForm()

    return render(
        request,
        "vehicles/vehicle_form.html",
        {"form": form}
    )


@role_required("STAFF", "ADMIN")
def vehicle_update(request, pk):

    vehicle = get_object_or_404(
        Vehicle,
        pk=pk
    )

    if request.method == "POST":

        form = VehicleForm(
            request.POST,
            request.FILES,
            instance=vehicle
        )

        if form.is_valid():
            form.save()
            messages.success(request, "Vehicle updated successfully.")
            return redirect("vehicles:list")

    else:

        form = VehicleForm(
            instance=vehicle
        )

    return render(
        request,
        "vehicles/vehicle_form.html",
        {"form": form}
    )


@role_required("STAFF", "ADMIN")
def vehicle_delete(request, pk):

    vehicle = get_object_or_404(
        Vehicle,
        pk=pk
    )

    if request.method == "POST":

        vehicle.delete()
        messages.success(request, "Vehicle deleted successfully.")
        return redirect("vehicles:list")

    return render(
        request,
        "vehicles/vehicle_confirm_delete.html",
        {
            "vehicle": vehicle
        }
    )