from django.urls import path
from . import views

app_name = "vehicles"

urlpatterns = [

    path(
        "",
        views.vehicle_list,
        name="list"
    ),

    path(
        "create/",
        views.vehicle_create,
        name="create"
    ),

    path(
        "<int:pk>/edit/",
        views.vehicle_update,
        name="update"
    ),

    path(
        "<int:pk>/delete/",
        views.vehicle_delete,
        name="delete"
    ),
]