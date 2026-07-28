from django.urls import path
from . import views

app_name = "bookings"

urlpatterns = [
    path("", views.booking_list, name="list"),
    path("create/", views.booking_create, name="create"),
    path("<int:pk>/edit/", views.booking_update, name="update"),
    path("<int:pk>/delete/", views.booking_delete, name="delete"),
    path("<int:pk>/ticket/", views.booking_ticket, name="ticket"),
    path("available-seats/<int:trip_id>/", views.available_seats, name="available_seats"),
]