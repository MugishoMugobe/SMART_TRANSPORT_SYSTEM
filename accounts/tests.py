from django.test import TestCase
from django.urls import reverse

from .models import Profile
from .test_utils import DEFAULT_PASSWORD, create_admin, create_passenger_user, create_staff


class RegistrationTests(TestCase):

    def test_register_creates_passenger_account(self):
        response = self.client.post(reverse("accounts:register"), {
            "first_name": "Amina",
            "last_name": "Nabirye",
            "username": "amina",
            "email": "amina@example.com",
            "password1": "Str0ngPassw0rd!",
            "password2": "Str0ngPassw0rd!",
        })

        # Successful registration logs the user in and redirects home.
        self.assertEqual(response.status_code, 302)

        profile = Profile.objects.get(user__username="amina")
        self.assertEqual(profile.role, "PASSENGER")

    def test_register_rejects_mismatched_passwords(self):
        response = self.client.post(reverse("accounts:register"), {
            "first_name": "Amina",
            "last_name": "Nabirye",
            "username": "amina2",
            "email": "amina2@example.com",
            "password1": "Str0ngPassw0rd!",
            "password2": "SomethingElse!",
        })

        self.assertEqual(response.status_code, 200)  # form redisplayed with errors
        self.assertFalse(Profile.objects.filter(user__username="amina2").exists())


class LoginTests(TestCase):

    def setUp(self):
        self.staff = create_staff("staff_login")
        self.passenger = create_passenger_user("passenger_login")
        self.admin = create_admin("admin_login")

    def test_valid_login_succeeds(self):
        response = self.client.post(reverse("accounts:login"), {
            "username": "staff_login",
            "password": DEFAULT_PASSWORD,
        })
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, "/dashboard/")

    def test_invalid_login_shows_error_and_does_not_log_in(self):
        response = self.client.post(reverse("accounts:login"), {
            "username": "staff_login",
            "password": "wrong-password",
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Incorrect username or password")
        self.assertNotIn("_auth_user_id", self.client.session)

    def test_admin_role_redirects_to_django_admin(self):
        response = self.client.post(reverse("accounts:login"), {
            "username": "admin_login",
            "password": DEFAULT_PASSWORD,
        })
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, "/admin/")

    def test_passenger_role_redirects_home(self):
        response = self.client.post(reverse("accounts:login"), {
            "username": "passenger_login",
            "password": DEFAULT_PASSWORD,
        })
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, "/")

    def test_logout_clears_session(self):
        self.client.login(username="staff_login", password=DEFAULT_PASSWORD)
        response = self.client.get(reverse("accounts:logout"))
        self.assertEqual(response.status_code, 302)
        self.assertNotIn("_auth_user_id", self.client.session)
