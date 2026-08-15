import datetime

from django.contrib.auth.models import User
from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework import serializers

from accounts.models import Profile
from bookings import services as booking_services
from bookings.models import Booking
from drivers.models import Driver
from passengers.models import Passenger
from routes.models import Route
from trips.models import Trip
from vehicles.models import Vehicle


class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ["role", "phone", "address"]


class CurrentUserSerializer(serializers.ModelSerializer):
    """Backs GET /api/v1/me/ — lets a frontend discover who is logged in
    and what role/permissions to render, without a second auth system."""

    profile = ProfileSerializer(read_only=True)

    class Meta:
        model = User
        fields = ["id", "username", "email", "first_name", "last_name", "is_superuser", "profile"]


class PassengerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Passenger
        fields = ["id", "full_name", "email", "phone", "address", "national_id", "created_at"]
        read_only_fields = ["created_at"]


class DriverSerializer(serializers.ModelSerializer):
    class Meta:
        model = Driver
        fields = ["id", "full_name", "phone", "license_number", "years_of_experience", "photo", "created_at"]
        read_only_fields = ["created_at"]


class VehicleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vehicle
        fields = [
            "id", "vehicle_number", "vehicle_type", "seating_capacity",
            "model", "manufacturer", "year", "image", "created_at",
        ]
        read_only_fields = ["created_at"]

    def validate_year(self, value):
        current_year = datetime.date.today().year
        if value < 1980 or value > current_year + 1:
            raise serializers.ValidationError(
                f"Enter a realistic year between 1980 and {current_year + 1}."
            )
        return value

    def validate_seating_capacity(self, value):
        if value < 1:
            raise serializers.ValidationError("Seating capacity must be at least 1.")
        return value


class RouteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Route
        fields = [
            "id", "origin", "destination", "distance", "estimated_duration",
            "fare", "status", "description", "created_at",
        ]
        read_only_fields = ["created_at"]

    def validate_fare(self, value):
        if value <= 0:
            raise serializers.ValidationError("Fare must be greater than zero.")
        return value

    def validate_distance(self, value):
        if value <= 0:
            raise serializers.ValidationError("Distance must be greater than zero.")
        return value

    def validate(self, attrs):
        origin = attrs.get("origin", getattr(self.instance, "origin", None))
        destination = attrs.get("destination", getattr(self.instance, "destination", None))
        if origin and destination and origin.strip().lower() == destination.strip().lower():
            raise serializers.ValidationError("Origin and destination must be different.")
        return attrs


class TripSerializer(serializers.ModelSerializer):
    vehicle_number = serializers.CharField(source="vehicle.vehicle_number", read_only=True)
    driver_name = serializers.CharField(source="driver.full_name", read_only=True)
    route_label = serializers.SerializerMethodField()

    class Meta:
        model = Trip
        fields = [
            "id", "trip_number", "vehicle", "vehicle_number", "driver", "driver_name",
            "route", "route_label", "departure_time", "arrival_time",
            "available_seats", "status", "notes", "created_at",
        ]
        read_only_fields = ["created_at", "available_seats"]

    def get_route_label(self, obj):
        return f"{obj.route.origin} → {obj.route.destination}"

    def validate(self, attrs):
        departure = attrs.get("departure_time", getattr(self.instance, "departure_time", None))
        arrival = attrs.get("arrival_time", getattr(self.instance, "arrival_time", None))
        if departure and arrival and arrival <= departure:
            raise serializers.ValidationError("Arrival time must be after departure time.")
        return attrs

    def create(self, validated_data):
        # A brand-new trip always starts with every seat on its vehicle free.
        vehicle = validated_data["vehicle"]
        validated_data["available_seats"] = vehicle.seating_capacity
        return super().create(validated_data)


class BookingSerializer(serializers.ModelSerializer):
    passenger_name = serializers.CharField(source="passenger.full_name", read_only=True)
    trip_label = serializers.CharField(source="trip.trip_number", read_only=True)

    class Meta:
        model = Booking
        fields = [
            "id", "booking_reference", "passenger", "passenger_name", "trip", "trip_label",
            "seat_number", "amount", "booking_date", "payment_status", "status", "qr_code",
        ]
        read_only_fields = ["booking_reference", "amount", "booking_date", "qr_code", "status"]

    def create(self, validated_data):
        try:
            return booking_services.create_booking(
                passenger=validated_data["passenger"],
                trip=validated_data["trip"],
                seat_number=validated_data.get("seat_number"),
            )
        except DjangoValidationError as exc:
            raise serializers.ValidationError({"seat_number": exc.messages})


class BookingCancelSerializer(serializers.Serializer):
    """Empty-bodied serializer for POST /bookings/{id}/cancel/ — exists so
    the action has a documented, validated request/response shape in the
    browsable API rather than accepting an arbitrary payload."""

    def save(self, **kwargs):
        return booking_services.cancel_booking(self.context["booking"])
