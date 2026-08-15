from django.urls import include, path
from rest_framework.routers import DefaultRouter

from . import views

app_name = "api"

router = DefaultRouter()
router.register("passengers", views.PassengerViewSet, basename="passenger")
router.register("drivers", views.DriverViewSet, basename="driver")
router.register("vehicles", views.VehicleViewSet, basename="vehicle")
router.register("routes", views.RouteViewSet, basename="route")
router.register("trips", views.TripViewSet, basename="trip")
router.register("bookings", views.BookingViewSet, basename="booking")

urlpatterns = [
    path("me/", views.CurrentUserView.as_view(), name="me"),
    path("", include(router.urls)),
]
