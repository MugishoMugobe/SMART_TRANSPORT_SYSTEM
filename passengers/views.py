from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from .models import Passenger
from .forms import PassengerForm
from django.contrib import messages


@login_required
def passenger_list(request):

    query = request.GET.get("q")

    passengers = Passenger.objects.all()

    if query:
        passengers = passengers.filter(
            full_name__icontains=query
        )

    paginator = Paginator(passengers, 10)

    page = request.GET.get("page")

    passengers = paginator.get_page(page)

    return render(
        request,
        "passengers/passenger_list.html",
        {
            "passengers": passengers,
            "query": query,
        }
    )


@login_required
def passenger_create(request):

    if request.method == "POST":
        form = PassengerForm(request.POST)

        if form.is_valid():
            form.save()
            return redirect("passengers:list")

    else:
        form = PassengerForm()

    return render(
        request,
        "passengers/passenger_form.html",
        {"form": form}
    )


@login_required
def passenger_update(request, pk):

    passenger = get_object_or_404(
        Passenger,
        pk=pk
    )

    if request.method == "POST":

        form = PassengerForm(
            request.POST,
            instance=passenger
        )

        if form.is_valid():
            form.save()
            messages.success(request, "Passenger added successfully.")
            return redirect("passengers:list")

    else:

        form = PassengerForm(
            instance=passenger
        )

    return render(
        request,
        "passengers/passenger_form.html",
        {"form": form}
    )


@login_required
def passenger_delete(request, pk):

    passenger = get_object_or_404(
        Passenger,
        pk=pk
    )

    if request.method == "POST":
        passenger.delete()
        messages.success(request, "Passenger deleted successfully.")
        return redirect("passengers:list")

    return render(
        request,
        "passengers/passenger_confirm_delete.html",
        {
            "passenger": passenger
        }
    )