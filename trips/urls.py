from django.urls import path
from . import views

app_name = "trips"

urlpatterns = [

    path(
        "",
        views.trip_list,
        name="list"
    ),

    path(
        "create/",
        views.trip_create,
        name="create"
    ),

    path(
        "<int:pk>/edit/",
        views.trip_update,
        name="update"
    ),

    path(
        "<int:pk>/delete/",
        views.trip_delete,
        name="delete"
    ),
]