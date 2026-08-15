from datetime import timedelta

from django.core.exceptions import ValidationError
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from accounts.test_utils import DEFAULT_PASSWORD, create_passenger_user, create_staff, tiny_image_file
from drivers.models import Driver
from passengers.models import Passenger
from routes.models import Route
from trips.models import Trip
from vehicles.models import Vehicle

from . import services
from .models import Booking


def make_trip(seats=2, **overrides):
    vehicle = Vehicle.objects.create(
        vehicle_number=overrides.pop("vehicle_number", "UAX-200T"),
        vehicle_type=Vehicle.BUS, seating_capacity=seats,
        model="Coaster", manufacturer="Toyota", year=2020, image=tiny_image_file(),
    )
    driver = Driver.objects.create(
        full_name="Musa Kato", phone="0700555666",
        license_number=overrides.pop("license_number", "LIC-200"),
        years_of_experience=5, photo=tiny_image_file(),
    )
    route = Route.objects.create(
        origin="Kampala", destination="Entebbe", distance="35.00",
        estimated_duration=timedelta(hours=1), fare="10000.00", status="ACTIVE",
    )
    now = timezone.now()
    fields = dict(
        trip_number=overrides.pop("trip_number", "TRIP-BK-0001"),
        vehicle=vehicle, driver=driver, route=route,
        departure_time=now + timedelta(hours=1),
        arrival_time=now + timedelta(hours=2),
        available_seats=seats,
        status="SCHEDULED",
    )
    fields.update(overrides)
    return Trip.objects.create(**fields)


class BookingServiceTests(TestCase):
    """Business rules live in services.py — test them directly, since
    both the HTML views and the REST API depend on this module."""

    def setUp(self):
        self.trip = make_trip(seats=1)
        self.passenger = Passenger.objects.create(
            full_name="Grace Auma", email="grace@example.com",
            phone="0700111222", national_id="ID-BK-0001",
        )

    def test_create_booking_generates_reference_and_decrements_seats(self):
        booking = services.create_booking(self.passenger, self.trip, seat_number=1)

        self.assertEqual(booking.booking_reference, "BK00001")
        self.assertEqual(booking.amount, self.trip.route.fare)

        self.trip.refresh_from_db()
        self.assertEqual(self.trip.available_seats, 0)

    def test_duplicate_seat_is_rejected(self):
        services.create_booking(self.passenger, self.trip, seat_number=1)

        second_passenger = Passenger.objects.create(
            full_name="Peter Okello", email="peter@example.com",
            phone="0700333444", national_id="ID-BK-0002",
        )

        with self.assertRaises(ValidationError):
            # trip only has 1 seat and it's taken — this should fail on
            # the "no seats available" check before it even reaches the
            # duplicate-seat check.
            services.create_booking(second_passenger, self.trip, seat_number=1)

    def test_overbooking_is_rejected(self):
        services.create_booking(self.passenger, self.trip, seat_number=1)
        self.trip.refresh_from_db()
        self.assertEqual(self.trip.available_seats, 0)

        second_passenger = Passenger.objects.create(
            full_name="Peter Okello", email="peter@example.com",
            phone="0700333444", national_id="ID-BK-0003",
        )

        with self.assertRaises(ValidationError) as ctx:
            services.create_booking(second_passenger, self.trip, seat_number=1)
        self.assertIn("No seats are available", str(ctx.exception))

    def test_seat_outside_capacity_is_rejected(self):
        with self.assertRaises(ValidationError):
            services.create_booking(self.passenger, self.trip, seat_number=99)

    def test_cancel_booking_frees_the_seat(self):
        booking = services.create_booking(self.passenger, self.trip, seat_number=1)
        self.trip.refresh_from_db()
        self.assertEqual(self.trip.available_seats, 0)

        services.cancel_booking(booking)

        self.trip.refresh_from_db()
        booking.refresh_from_db()
        self.assertEqual(self.trip.available_seats, 1)
        self.assertEqual(booking.status, "CANCELLED")

    def test_cancelling_twice_does_not_double_credit_the_seat(self):
        booking = services.create_booking(self.passenger, self.trip, seat_number=1)

        services.cancel_booking(booking)
        services.cancel_booking(booking)

        self.trip.refresh_from_db()
        self.assertEqual(self.trip.available_seats, 1)  # not 2


class BookingViewRBACTests(TestCase):
    """A PASSENGER account may create bookings and see/cancel only their
    own; STAFF/ADMIN manage every booking."""

    def setUp(self):
        self.trip = make_trip(seats=3)

        self.rider_user = create_passenger_user("rider_bk", email="rider@example.com")
        self.other_user = create_passenger_user("other_bk", email="other@example.com")
        create_staff("staff_bk")

        self.rider_passenger = Passenger.objects.create(
            full_name="Rider", email="rider@example.com", phone="0700000001",
            national_id="ID-RIDER",
        )
        self.other_passenger = Passenger.objects.create(
            full_name="Other", email="other@example.com", phone="0700000002",
            national_id="ID-OTHER",
        )

        self.own_booking = services.create_booking(self.rider_passenger, self.trip, 1)
        self.foreign_booking = services.create_booking(self.other_passenger, self.trip, 2)

    def test_passenger_only_sees_own_booking_in_list(self):
        self.client.login(username="rider_bk", password=DEFAULT_PASSWORD)
        response = self.client.get(reverse("bookings:list"))

        self.assertContains(response, self.own_booking.booking_reference)
        self.assertNotContains(response, self.foreign_booking.booking_reference)

    def test_staff_sees_every_booking(self):
        self.client.login(username="staff_bk", password=DEFAULT_PASSWORD)
        response = self.client.get(reverse("bookings:list"))

        self.assertContains(response, self.own_booking.booking_reference)
        self.assertContains(response, self.foreign_booking.booking_reference)

    def test_passenger_cannot_cancel_someone_elses_booking(self):
        self.client.login(username="rider_bk", password=DEFAULT_PASSWORD)
        self.client.post(reverse("bookings:cancel", args=[self.foreign_booking.pk]))

        self.foreign_booking.refresh_from_db()
        self.assertEqual(self.foreign_booking.status, "CONFIRMED")  # unchanged

    def test_passenger_can_cancel_own_booking(self):
        self.client.login(username="rider_bk", password=DEFAULT_PASSWORD)
        self.client.post(reverse("bookings:cancel", args=[self.own_booking.pk]))

        self.own_booking.refresh_from_db()
        self.assertEqual(self.own_booking.status, "CANCELLED")

    def test_passenger_cannot_hard_delete_a_booking(self):
        self.client.login(username="rider_bk", password=DEFAULT_PASSWORD)
        response = self.client.post(reverse("bookings:delete", args=[self.own_booking.pk]))

        self.assertEqual(response.status_code, 302)  # bounced by role_required
        self.assertTrue(Booking.objects.filter(pk=self.own_booking.pk).exists())
