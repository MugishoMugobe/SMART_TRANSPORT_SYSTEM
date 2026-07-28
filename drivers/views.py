from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator

from .models import Driver
from .forms import DriverForm


@login_required
def driver_list(request):

    query = request.GET.get("q")

    drivers = Driver.objects.all()

    if query:
        drivers = drivers.filter(
            full_name__icontains=query
        )

    paginator = Paginator(drivers, 10)

    page = request.GET.get("page")

    drivers = paginator.get_page(page)

    return render(
        request,
        "drivers/driver_list.html",
        {
            "drivers": drivers,
            "query": query
        }
    )


@login_required
def driver_create(request):

    if request.method == "POST":

        form = DriverForm(
            request.POST,
            request.FILES
        )

        if form.is_valid():
            form.save()
            return redirect("drivers:list")

    else:
        form = DriverForm()

    return render(
        request,
        "drivers/driver_form.html",
        {"form": form}
    )


@login_required
def driver_update(request, pk):

    driver = get_object_or_404(
        Driver,
        pk=pk
    )

    if request.method == "POST":

        form = DriverForm(
            request.POST,
            request.FILES,
            instance=driver
        )

        if form.is_valid():
            form.save()
            return redirect("drivers:list")

    else:

        form = DriverForm(
            instance=driver
        )

    return render(
        request,
        "drivers/driver_form.html",
        {"form": form}
    )


@login_required
def driver_delete(request, pk):

    driver = get_object_or_404(
        Driver,
        pk=pk
    )

    if request.method == "POST":
        driver.delete()
        return redirect("drivers:list")

    return render(
        request,
        "drivers/driver_confirm_delete.html",
        {
            "driver": driver
        }
    )