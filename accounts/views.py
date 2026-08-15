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
        remember_me = request.POST.get("remember")

        user = authenticate(
            request,
            username=username,
            password=password
        )

        if user:
            login(request, user)

            # Stay signed in after the browser closes only if requested.
            if remember_me:
                request.session.set_expiry(1209600)  # 2 weeks
            else:
                request.session.set_expiry(0)

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

        return render(request, "accounts/login.html", {
            "error": "Incorrect username or password. Please try again.",
            "username": username,
        })

    return render(request, "accounts/login.html")


def user_logout(request):
    logout(request)
    return redirect("accounts:login")