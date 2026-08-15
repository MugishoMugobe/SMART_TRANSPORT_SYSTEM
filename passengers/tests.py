from django.test import TestCase
from django.urls import reverse

from accounts.test_utils import DEFAULT_PASSWORD, create_passenger_user, create_staff
from .models import Passenger


class PassengerCRUDTests(TestCase):
    """Full-module CRUD, exercised as a STAFF account."""

    def setUp(self):
        self.staff = create_staff("staff_passengers")
        self.client.login(username="staff_passengers", password=DEFAULT_PASSWORD)
        self.passenger = Passenger.objects.create(
            full_name="Grace Auma",
            email="grace@example.com",
            phone="0700111222",
            national_id="ID-0001",
        )

    def test_list_shows_seeded_passenger(self):
        response = self.client.get(reverse("passengers:list"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Grace Auma")

    def test_search_filters_by_name(self):
        response = self.client.get(reverse("passengers:list"), {"q": "Auma"})
        self.assertContains(response, "Grace Auma")

        response = self.client.get(reverse("passengers:list"), {"q": "Nobody"})
        self.assertNotContains(response, "Grace Auma")

    def test_create_passenger(self):
        response = self.client.post(reverse("passengers:create"), {
            "full_name": "Peter Okello",
            "email": "peter@example.com",
            "phone": "0700333444",
            "address": "Kampala",
            "national_id": "ID-0002",
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Passenger.objects.filter(national_id="ID-0002").exists())

    def test_update_passenger(self):
        response = self.client.post(
            reverse("passengers:update", args=[self.passenger.pk]),
            {
                "full_name": "Grace A. Auma",
                "email": "grace@example.com",
                "phone": "0700111222",
                "address": "",
                "national_id": "ID-0001",
            },
        )
        self.assertEqual(response.status_code, 302)
        self.passenger.refresh_from_db()
        self.assertEqual(self.passenger.full_name, "Grace A. Auma")

    def test_delete_passenger(self):
        response = self.client.post(reverse("passengers:delete", args=[self.passenger.pk]))
        self.assertEqual(response.status_code, 302)
        self.assertFalse(Passenger.objects.filter(pk=self.passenger.pk).exists())


class PassengerRBACTests(TestCase):
    """Passenger records hold PII — a PASSENGER-role account must be
    bounced from every view in this module, including plain read."""

    def setUp(self):
        create_passenger_user("rider")
        self.client.login(username="rider", password=DEFAULT_PASSWORD)
        self.passenger = Passenger.objects.create(
            full_name="Grace Auma", email="grace@example.com",
            phone="0700111222", national_id="ID-0001",
        )

    def test_passenger_role_blocked_from_list(self):
        response = self.client.get(reverse("passengers:list"))
        self.assertEqual(response.status_code, 302)  # bounced, not shown the data

    def test_passenger_role_blocked_from_create(self):
        response = self.client.post(reverse("passengers:create"), {
            "full_name": "Should Not Save",
            "email": "nope@example.com",
            "phone": "0700000000",
            "national_id": "ID-9999",
        })
        self.assertEqual(response.status_code, 302)
        self.assertFalse(Passenger.objects.filter(national_id="ID-9999").exists())

    def test_passenger_role_blocked_from_delete(self):
        response = self.client.post(reverse("passengers:delete", args=[self.passenger.pk]))
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Passenger.objects.filter(pk=self.passenger.pk).exists())

    def test_anonymous_redirected_to_login(self):
        self.client.logout()
        response = self.client.get(reverse("passengers:list"))
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse("accounts:login"), response.url)
