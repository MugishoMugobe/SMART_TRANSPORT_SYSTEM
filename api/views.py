from rest_framework import filters, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from bookings.models import Booking
from drivers.models import Driver
from passengers.models import Passenger
from routes.models import Route
from trips.models import Trip
from vehicles.models import Vehicle

from .permissions import (
    BookingAccessPermission,
    IsStaffAdminOrReadOnly,
    IsStaffOrAdmin,
    is_staff_or_admin,
)
from .serializers import (
    BookingCancelSerializer,
    BookingSerializer,
    CurrentUserSerializer,
    DriverSerializer,
    PassengerSerializer,
    RouteSerializer,
    TripSerializer,
    VehicleSerializer,
)


class CurrentUserView(APIView):
    """GET /api/v1/me/ — who am I, and what role/permissions do I have.
    Lets any client (this app's own JS, a mobile app, Postman) discover
    the logged-in user's role without duplicating the login flow."""

    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response(CurrentUserSerializer(request.user).data)


class PassengerViewSet(viewsets.ModelViewSet):
    """Passenger records hold personal data (national ID, contact info),
    so — unlike vehicles/routes/trips — even *reading* this endpoint is
    staff/admin only."""

    queryset = Passenger.objects.all()
    serializer_class = PassengerSerializer
    permission_classes = [IsStaffOrAdmin]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["full_name", "email", "phone", "national_id"]
    ordering_fields = ["full_name", "created_at"]


class DriverViewSet(viewsets.ModelViewSet):
    queryset = Driver.objects.all()
    serializer_class = DriverSerializer
    permission_classes = [IsStaffOrAdmin]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["full_name", "license_number", "phone"]
    ordering_fields = ["full_name", "years_of_experience", "created_at"]


class VehicleViewSet(viewsets.ModelViewSet):
    """Read is open to any authenticated user — a passenger browsing
    trips needs to see vehicle type/capacity — writes are staff/admin."""

    serializer_class = VehicleSerializer
    permission_classes = [IsStaffAdminOrReadOnly]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["vehicle_number", "manufacturer", "model"]
    ordering_fields = ["vehicle_number", "year", "seating_capacity"]

    def get_queryset(self):
        queryset = Vehicle.objects.all()
        vehicle_type = self.request.query_params.get("vehicle_type")
        if vehicle_type:
            queryset = queryset.filter(vehicle_type=vehicle_type)
        return queryset


class RouteViewSet(viewsets.ModelViewSet):
    serializer_class = RouteSerializer
    permission_classes = [IsStaffAdminOrReadOnly]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["origin", "destination"]
    ordering_fields = ["fare", "distance", "created_at"]

    def get_queryset(self):
        queryset = Route.objects.all()
        status_param = self.request.query_params.get("status")
        if status_param:
            queryset = queryset.filter(status=status_param)
        return queryset


class TripViewSet(viewsets.ModelViewSet):
    serializer_class = TripSerializer
    permission_classes = [IsStaffAdminOrReadOnly]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = [
        "trip_number", "vehicle__vehicle_number", "driver__full_name",
        "route__origin", "route__destination",
    ]
    ordering_fields = ["departure_time", "arrival_time", "available_seats"]

    def get_queryset(self):
        queryset = Trip.objects.select_related("vehicle", "driver", "route")
        status_param = self.request.query_params.get("status")
        if status_param:
            queryset = queryset.filter(status=status_param)
        return queryset


class BookingViewSet(viewsets.ModelViewSet):
    """
    STAFF/ADMIN see and manage every booking.
    A PASSENGER-role user only ever sees bookings tied to a passenger
    record sharing their account email — enforced here in the queryset
    (so it never even appears in a list) and again in
    BookingAccessPermission (so a guessed detail URL 404s the same way).
    """

    serializer_class = BookingSerializer
    permission_classes = [BookingAccessPermission]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["booking_reference", "passenger__full_name", "trip__trip_number"]
    ordering_fields = ["booking_date", "amount"]

    def get_queryset(self):
        queryset = Booking.objects.select_related("passenger", "trip")

        status_param = self.request.query_params.get("status")
        if status_param:
            queryset = queryset.filter(status=status_param)

        if is_staff_or_admin(self.request.user):
            return queryset

        return queryset.filter(passenger__email__iexact=self.request.user.email or "")

    @action(detail=True, methods=["post"])
    def cancel(self, request, pk=None):
        booking = self.get_object()
        serializer = BookingCancelSerializer(data={}, context={"booking": booking})
        serializer.is_valid(raise_exception=True)
        booking = serializer.save()
        return Response(BookingSerializer(booking).data)
