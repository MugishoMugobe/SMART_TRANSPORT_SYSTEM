from django.urls import path
from . import views

app_name = "routes"

urlpatterns = [

    path("", views.route_list, name="list"),

    path(
        "create/",
        views.route_create,
        name="create"
    ),

    path(
        "<int:pk>/edit/",
        views.route_update,
        name="update"
    ),

    path(
        "<int:pk>/delete/",
        views.route_delete,
        name="delete"
    ),
]