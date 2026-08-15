from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator

from .models import Route
from .forms import RouteForm
from django.db.models import Q
from accounts.decorators import role_required


@login_required
def route_list(request):

    query = request.GET.get("q")

    routes = Route.objects.all()

    if query:
        routes = routes.filter(
            Q(origin__icontains=query) |
            Q(destination__icontains=query)
    )

    status = request.GET.get("status")

    if status:
        routes = routes.filter(status=status)

    paginator = Paginator(routes, 10)

    page = request.GET.get("page")

    routes = paginator.get_page(page)

    return render(
        request,
        "routes/route_list.html",
        {
            "routes": routes,
            "query": query,
            "status": status,
            "status_choices": Route.STATUS_CHOICES,
        }
    )


@role_required("STAFF", "ADMIN")
def route_create(request):

    if request.method == "POST":

        form = RouteForm(request.POST)

        if form.is_valid():

            form.save()

            messages.success(
                request,
                "Route created successfully."
            )

            return redirect("routes:list")

    else:

        form = RouteForm()

    return render(
        request,
        "routes/route_form.html",
        {
            "form": form
        }
    )


@role_required("STAFF", "ADMIN")
def route_update(request, pk):

    route = get_object_or_404(Route, pk=pk)

    if request.method == "POST":

        form = RouteForm(
            request.POST,
            instance=route
        )

        if form.is_valid():

            form.save()

            messages.success(
                request,
                "Route updated successfully."
            )

            return redirect("routes:list")

    else:

        form = RouteForm(instance=route)

    return render(
        request,
        "routes/route_form.html",
        {
            "form": form
        }
    )


@role_required("STAFF", "ADMIN")
def route_delete(request, pk):

    route = get_object_or_404(Route, pk=pk)

    if request.method == "POST":

        route.delete()

        messages.success(
            request,
            "Route deleted successfully."
        )

        return redirect("routes:list")

    return render(
        request,
        "routes/route_confirm_delete.html",
        {
            "route": route
        }
    )