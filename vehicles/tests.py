from django.test import TestCase
from django.urls import reverse

from accounts.test_utils import DEFAULT_PASSWORD, create_passenger_user, create_staff, tiny_image_file
from .models import Vehicle


def make_vehicle(**overrides):
    fields = dict(
        vehicle_number="UAX-001T",
        vehicle_type=Vehicle.BUS,
        seating_capacity=30,
        model="Coaster",
        manufacturer="Toyota",
        year=2020,
        image=tiny_image_file(),
    )
    fields.update(overrides)
    return Vehicle.objects.create(**fields)


class VehicleCRUDTests(TestCase):

    def setUp(self):
        create_staff("staff_vehicles")
        self.client.login(username="staff_vehicles", password=DEFAULT_PASSWORD)
        self.vehicle = make_vehicle()

    def test_create_vehicle(self):
        response = self.client.post(reverse("vehicles:create"), {
            "vehicle_number": "UAX-002T",
            "vehicle_type": Vehicle.MINIBUS,
            "seating_capacity": 14,
            "manufacturer": "Nissan",
            "model": "Caravan",
            "year": 2019,
            "image": tiny_image_file(),
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Vehicle.objects.filter(vehicle_number="UAX-002T").exists())

    def test_filter_by_vehicle_type(self):
        make_vehicle(vehicle_number="UAX-003T", vehicle_type=Vehicle.TAXI)

        response = self.client.get(reverse("vehicles:list"), {"vehicle_type": Vehicle.TAXI})
        self.assertContains(response, "UAX-003T")
        self.assertNotContains(response, "UAX-001T")

    def test_delete_vehicle(self):
        response = self.client.post(reverse("vehicles:delete", args=[self.vehicle.pk]))
        self.assertEqual(response.status_code, 302)
        self.assertFalse(Vehicle.objects.filter(pk=self.vehicle.pk).exists())


class VehicleRBACTests(TestCase):
    """Vehicles aren't personal data — any authenticated role can browse
    the fleet, but only staff/admin can change it."""

    def setUp(self):
        create_passenger_user("rider_v")
        self.client.login(username="rider_v", password=DEFAULT_PASSWORD)
        self.vehicle = make_vehicle()

    def test_passenger_can_read_list(self):
        response = self.client.get(reverse("vehicles:list"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "UAX-001T")

    def test_passenger_cannot_create(self):
        response = self.client.post(reverse("vehicles:create"), {
            "vehicle_number": "SHOULD-NOT-EXIST",
            "vehicle_type": Vehicle.BUS,
            "seating_capacity": 10,
            "manufacturer": "X",
            "model": "Y",
            "year": 2020,
            "image": tiny_image_file(),
        })
        self.assertEqual(response.status_code, 302)
        self.assertFalse(Vehicle.objects.filter(vehicle_number="SHOULD-NOT-EXIST").exists())

    def test_passenger_cannot_delete(self):
        response = self.client.post(reverse("vehicles:delete", args=[self.vehicle.pk]))
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Vehicle.objects.filter(pk=self.vehicle.pk).exists())
