from django.urls import path
from . import views

app_name = "drivers"

urlpatterns = [
    path("", views.driver_list, name="list"),
    path("create/", views.driver_create, name="create"),
    path("<int:pk>/edit/", views.driver_update, name="update"),
    path("<int:pk>/delete/", views.driver_delete, name="delete"),
]