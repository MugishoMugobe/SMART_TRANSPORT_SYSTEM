from datetime import timedelta

from django.test import TestCase
from django.urls import reverse

from accounts.test_utils import DEFAULT_PASSWORD, create_passenger_user, create_staff
from .models import Route


def make_route(**overrides):
    fields = dict(
        origin="Kampala",
        destination="Entebbe",
        distance="35.00",
        estimated_duration=timedelta(hours=1),
        fare="10000.00",
        status="ACTIVE",
    )
    fields.update(overrides)
    return Route.objects.create(**fields)


class RouteCRUDTests(TestCase):

    def setUp(self):
        create_staff("staff_routes")
        self.client.login(username="staff_routes", password=DEFAULT_PASSWORD)
        self.route = make_route()

    def test_create_route(self):
        response = self.client.post(reverse("routes:create"), {
            "origin": "Kampala",
            "destination": "Jinja",
            "distance": "80.00",
            "estimated_duration": "02:00",
            "fare": "20000.00",
            "status": "ACTIVE",
            "description": "",
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Route.objects.filter(destination="Jinja").exists())

    def test_filter_by_status(self):
        make_route(origin="Mbale", destination="Soroti", status="INACTIVE")

        response = self.client.get(reverse("routes:list"), {"status": "INACTIVE"})
        self.assertContains(response, "Soroti")
        self.assertNotContains(response, "Entebbe")

    def test_delete_route(self):
        response = self.client.post(reverse("routes:delete", args=[self.route.pk]))
        self.assertEqual(response.status_code, 302)
        self.assertFalse(Route.objects.filter(pk=self.route.pk).exists())


class RouteRBACTests(TestCase):

    def setUp(self):
        create_passenger_user("rider_r")
        self.client.login(username="rider_r", password=DEFAULT_PASSWORD)
        self.route = make_route()

    def test_passenger_can_read_list(self):
        response = self.client.get(reverse("routes:list"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Entebbe")

    def test_passenger_cannot_create(self):
        response = self.client.post(reverse("routes:create"), {
            "origin": "A", "destination": "B", "distance": "1.00",
            "estimated_duration": "00:10", "fare": "1000.00", "status": "ACTIVE",
        })
        self.assertEqual(response.status_code, 302)
        self.assertFalse(Route.objects.filter(origin="A").exists())
