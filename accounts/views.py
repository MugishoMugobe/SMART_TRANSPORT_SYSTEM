from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from .forms import RegisterForm


def register(request):
    if request.method == "POST":
        form = RegisterForm(request.POST)

        if form.is_valid():
            user = form.save()

             # Update the automatically created profile
            user.profile.role = "PASSENGER"
            user.profile.save()

            login(request, user)
            return redirect("/")

    else:
        form = RegisterForm()

    return render(request, "accounts/register.html", {
        "form": form
    })


def user_login(request):

    if request.method == "POST":

        username = request.POST["username"]
        password = request.POST["password"]

        user = authenticate(
            request,
            username=username,
            password=password
        )

        if user:
            login(request, user)

            # Role-based redirection
            """
           if user.is_superuser:
                return redirect("/admin/")

            elif user.groups.filter(name="Staff").exists():
                return redirect("/dashboard/")

            elif user.groups.filter(name="Passenger").exists():
                return redirect("/")

            return redirect("/")"""
            if user.is_superuser:
                return redirect("/admin/")

            role = user.profile.role

            if role == "ADMIN":
                return redirect("/admin/")

            elif role == "STAFF":
                return redirect("/dashboard/")

            elif role == "PASSENGER":
                return redirect("/")

            return redirect("/")

    return render(request, "accounts/login.html")


def user_logout(request):
    logout(request)
    return redirect("accounts:login")