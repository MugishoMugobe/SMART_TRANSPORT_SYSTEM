from django.urls import path
from . import views

app_name = "passengers"

urlpatterns = [

    path(
        "",
        views.passenger_list,
        name="list"
    ),

    path(
        "create/",
        views.passenger_create,
        name="create"
    ),

    path(
        "<int:pk>/edit/",
        views.passenger_update,
        name="update"
    ),

    path(
        "<int:pk>/delete/",
        views.passenger_delete,
        name="delete"
    ),

]