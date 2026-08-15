from django.test import TestCase
from django.urls import reverse

from accounts.test_utils import DEFAULT_PASSWORD, create_passenger_user, create_staff, tiny_image_file
from .models import Driver


class DriverCRUDTests(TestCase):

    def setUp(self):
        create_staff("staff_drivers")
        self.client.login(username="staff_drivers", password=DEFAULT_PASSWORD)
        self.driver = Driver.objects.create(
            full_name="Musa Kato",
            phone="0700555666",
            license_number="LIC-0001",
            years_of_experience=5,
            photo=tiny_image_file(),
        )

    def test_list_shows_seeded_driver(self):
        response = self.client.get(reverse("drivers:list"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Musa Kato")

    def test_create_driver(self):
        response = self.client.post(reverse("drivers:create"), {
            "full_name": "Sarah Nakato",
            "phone": "0700777888",
            "license_number": "LIC-0002",
            "years_of_experience": 3,
            "photo": tiny_image_file(),
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Driver.objects.filter(license_number="LIC-0002").exists())

    def test_update_driver(self):
        response = self.client.post(
            reverse("drivers:update", args=[self.driver.pk]),
            {
                "full_name": "Musa Kato",
                "phone": "0700555666",
                "license_number": "LIC-0001",
                "years_of_experience": 6,
                "photo": tiny_image_file(),
            },
        )
        self.assertEqual(response.status_code, 302)
        self.driver.refresh_from_db()
        self.assertEqual(self.driver.years_of_experience, 6)

    def test_delete_driver(self):
        response = self.client.post(reverse("drivers:delete", args=[self.driver.pk]))
        self.assertEqual(response.status_code, 302)
        self.assertFalse(Driver.objects.filter(pk=self.driver.pk).exists())


class DriverRBACTests(TestCase):

    def setUp(self):
        create_passenger_user("rider_d")
        self.client.login(username="rider_d", password=DEFAULT_PASSWORD)

    def test_passenger_role_blocked_from_list(self):
        response = self.client.get(reverse("drivers:list"))
        self.assertEqual(response.status_code, 302)

    def test_passenger_role_blocked_from_create(self):
        response = self.client.post(reverse("drivers:create"), {
            "full_name": "Should Not Save",
            "phone": "0700000000",
            "license_number": "LIC-9999",
            "years_of_experience": 1,
            "photo": tiny_image_file(),
        })
        self.assertEqual(response.status_code, 302)
        self.assertFalse(Driver.objects.filter(license_number="LIC-9999").exists())
