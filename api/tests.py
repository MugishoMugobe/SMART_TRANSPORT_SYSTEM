from datetime import timedelta

from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase

from accounts.test_utils import (
    DEFAULT_PASSWORD, create_admin, create_passenger_user, create_staff, tiny_image_file,
)
from drivers.models import Driver
from passengers.models import Passenger
from routes.models import Route
from trips.models import Trip
from vehicles.models import Vehicle


class APIRoleAccessTests(APITestCase):
    """The API enforces the exact same roles as the HTML views — this is
    the automated version of the manual curl walkthrough used to build
    it, kept here so a regression fails CI instead of a demo."""

    def setUp(self):
        self.staff = create_staff("api_staff")
        self.passenger_user = create_passenger_user("api_passenger", email="rider@example.com")

        self.vehicle = Vehicle.objects.create(
            vehicle_number="UAX-300T", vehicle_type=Vehicle.BUS, seating_capacity=4,
            model="Coaster", manufacturer="Toyota", year=2021, image=tiny_image_file(),
        )

    def test_anonymous_request_gets_error_envelope(self):
        response = self.client.get(reverse("api:vehicle-list"))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data["error"]["code"], "not_authenticated")

    def test_passenger_can_read_vehicles(self):
        self.client.login(username="api_passenger", password=DEFAULT_PASSWORD)
        response = self.client.get(reverse("api:vehicle-list"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_passenger_cannot_write_vehicles(self):
        self.client.login(username="api_passenger", password=DEFAULT_PASSWORD)
        response = self.client.post(reverse("api:vehicle-list"), {
            "vehicle_number": "SHOULD-FAIL", "vehicle_type": Vehicle.BUS,
            "seating_capacity": 10, "model": "X", "manufacturer": "Y", "year": 2020,
        })
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data["error"]["code"], "permission_denied")

    def test_staff_can_write_vehicles(self):
        self.client.login(username="api_staff", password=DEFAULT_PASSWORD)
        response = self.client.post(reverse("api:vehicle-list"), {
            "vehicle_number": "UAX-301T", "vehicle_type": Vehicle.BUS,
            "seating_capacity": 10, "model": "X", "manufacturer": "Y", "year": 2020,
            "image": tiny_image_file(),
        }, format="multipart")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_passenger_cannot_read_passenger_pii(self):
        Passenger.objects.create(
            full_name="Grace Auma", email="grace@example.com",
            phone="0700111222", national_id="ID-API-0001",
        )
        self.client.login(username="api_passenger", password=DEFAULT_PASSWORD)
        response = self.client.get(reverse("api:passenger-list"))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_staff_can_read_passenger_pii(self):
        Passenger.objects.create(
            full_name="Grace Auma", email="grace@example.com",
            phone="0700111222", national_id="ID-API-0002",
        )
        self.client.login(username="api_staff", password=DEFAULT_PASSWORD)
        response = self.client.get(reverse("api:passenger-list"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)

    def test_me_endpoint_reports_role(self):
        self.client.login(username="api_staff", password=DEFAULT_PASSWORD)
        response = self.client.get(reverse("api:me"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["profile"]["role"], "STAFF")


class APIBookingTests(APITestCase):

    def setUp(self):
        self.passenger_user = create_passenger_user("api_rider", email="rider@example.com")
        self.staff = create_staff("api_bk_staff")

        self.passenger = Passenger.objects.create(
            full_name="Rider", email="rider@example.com", phone="0700000001",
            national_id="ID-API-RIDER",
        )
        vehicle = Vehicle.objects.create(
            vehicle_number="UAX-400T", vehicle_type=Vehicle.BUS, seating_capacity=2,
            model="Coaster", manufacturer="Toyota", year=2021, image=tiny_image_file(),
        )
        driver = Driver.objects.create(
            full_name="Driver X", phone="0700999999", license_number="LIC-API-1",
            years_of_experience=4, photo=tiny_image_file(),
        )
        route = Route.objects.create(
            origin="Kampala", destination="Gulu", distance="300.00",
            estimated_duration=timedelta(hours=5), fare="45000.00", status="ACTIVE",
        )
        now = timezone.now()
        self.trip = Trip.objects.create(
            trip_number="TRIP-API-0001", vehicle=vehicle, driver=driver, route=route,
            departure_time=now + timedelta(hours=1), arrival_time=now + timedelta(hours=6),
            available_seats=2, status="SCHEDULED",
        )

    def test_passenger_can_book_and_gets_reference(self):
        self.client.login(username="api_rider", password=DEFAULT_PASSWORD)
        response = self.client.post(reverse("api:booking-list"), {
            "passenger": self.passenger.id, "trip": self.trip.id, "seat_number": 1,
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(response.data["booking_reference"].startswith("BK"))

    def test_duplicate_seat_returns_validation_error_envelope(self):
        self.client.login(username="api_rider", password=DEFAULT_PASSWORD)
        self.client.post(reverse("api:booking-list"), {
            "passenger": self.passenger.id, "trip": self.trip.id, "seat_number": 1,
        })
        response = self.client.post(reverse("api:booking-list"), {
            "passenger": self.passenger.id, "trip": self.trip.id, "seat_number": 1,
        })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["error"]["code"], "validation_error")

    def test_passenger_booking_list_is_scoped_to_own_bookings(self):
        other_user = create_passenger_user("api_other", email="other@example.com")
        other_passenger = Passenger.objects.create(
            full_name="Other", email="other@example.com", phone="0700000002",
            national_id="ID-API-OTHER",
        )

        self.client.login(username="api_rider", password=DEFAULT_PASSWORD)
        self.client.post(reverse("api:booking-list"), {
            "passenger": self.passenger.id, "trip": self.trip.id, "seat_number": 1,
        })
        self.client.logout()

        self.client.login(username="api_other", password=DEFAULT_PASSWORD)
        self.client.post(reverse("api:booking-list"), {
            "passenger": other_passenger.id, "trip": self.trip.id, "seat_number": 2,
        })

        response = self.client.get(reverse("api:booking-list"))
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(response.data["results"][0]["passenger"], other_passenger.id)

    def test_cancel_action_frees_the_seat(self):
        self.client.login(username="api_rider", password=DEFAULT_PASSWORD)
        create_response = self.client.post(reverse("api:booking-list"), {
            "passenger": self.passenger.id, "trip": self.trip.id, "seat_number": 1,
        })
        booking_id = create_response.data["id"]

        response = self.client.post(reverse("api:booking-cancel", args=[booking_id]))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["status"], "CANCELLED")

        self.trip.refresh_from_db()
        self.assertEqual(self.trip.available_seats, 2)
