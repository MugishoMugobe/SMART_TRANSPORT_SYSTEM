import itertools
from datetime import timedelta

from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from accounts.test_utils import DEFAULT_PASSWORD, create_passenger_user, create_staff, tiny_image_file
from drivers.models import Driver
from routes.models import Route
from vehicles.models import Vehicle
from .models import Trip

_unique = itertools.count(1)


def make_trip(**overrides):
    n = next(_unique)

    vehicle = overrides.pop("vehicle", None) or Vehicle.objects.create(
        vehicle_number=f"UAX-{100 + n}T", vehicle_type=Vehicle.BUS, seating_capacity=30,
        model="Coaster", manufacturer="Toyota", year=2020, image=tiny_image_file(),
    )
    driver = overrides.pop("driver", None) or Driver.objects.create(
        full_name="Musa Kato", phone="0700555666", license_number=f"LIC-{100 + n}",
        years_of_experience=5, photo=tiny_image_file(),
    )
    route = overrides.pop("route", None) or Route.objects.create(
        origin="Kampala", destination="Entebbe", distance="35.00",
        estimated_duration=timedelta(hours=1), fare="10000.00", status="ACTIVE",
    )

    now = timezone.now()
    fields = dict(
        trip_number="TRIP-0001",
        vehicle=vehicle,
        driver=driver,
        route=route,
        departure_time=now + timedelta(hours=1),
        arrival_time=now + timedelta(hours=2),
        available_seats=vehicle.seating_capacity,
        status="SCHEDULED",
    )
    fields.update(overrides)
    return Trip.objects.create(**fields)


class TripCRUDTests(TestCase):

    def setUp(self):
        create_staff("staff_trips")
        self.client.login(username="staff_trips", password=DEFAULT_PASSWORD)
        self.trip = make_trip()

    def test_create_trip_seeds_available_seats_from_vehicle(self):
        response = self.client.post(reverse("trips:create"), {
            "trip_number": "TRIP-0002",
            "vehicle": self.trip.vehicle_id,
            "driver": self.trip.driver_id,
            "route": self.trip.route_id,
            "departure_time": (timezone.now() + timedelta(days=1)).strftime("%Y-%m-%dT%H:%M"),
            "arrival_time": (timezone.now() + timedelta(days=1, hours=1)).strftime("%Y-%m-%dT%H:%M"),
            "available_seats": 0,  # deliberately wrong — the view should overwrite this
            "status": "SCHEDULED",
        })
        self.assertEqual(response.status_code, 302)
        trip = Trip.objects.get(trip_number="TRIP-0002")
        self.assertEqual(trip.available_seats, trip.vehicle.seating_capacity)

    def test_filter_by_status(self):
        make_trip(trip_number="TRIP-0003", status="CANCELLED")

        response = self.client.get(reverse("trips:list"), {"status": "CANCELLED"})
        self.assertContains(response, "TRIP-0003")
        self.assertNotContains(response, "TRIP-0001")

    def test_delete_trip(self):
        response = self.client.post(reverse("trips:delete", args=[self.trip.pk]))
        self.assertEqual(response.status_code, 302)
        self.assertFalse(Trip.objects.filter(pk=self.trip.pk).exists())


class TripRBACTests(TestCase):

    def setUp(self):
        create_passenger_user("rider_t")
        self.client.login(username="rider_t", password=DEFAULT_PASSWORD)
        self.trip = make_trip()

    def test_passenger_can_read_list(self):
        response = self.client.get(reverse("trips:list"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "TRIP-0001")

    def test_passenger_cannot_delete(self):
        response = self.client.post(reverse("trips:delete", args=[self.trip.pk]))
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Trip.objects.filter(pk=self.trip.pk).exists())
