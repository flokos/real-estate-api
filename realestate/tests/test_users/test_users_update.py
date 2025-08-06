from rest_framework import status
from rest_framework.test import APIClient
from django.core.management import call_command
from ...models import User
from django.test import TestCase

class UsersListTests(TestCase):
    def setUp(self):
        call_command('flush', '--noinput')
        self.admin = User.objects.create_superuser(username="admin", password="pass")
        self.user = User.objects.create_user(username="user1", password="pass")
        self.other_user = User.objects.create_user(username="user2", password="pass")
        self.client = APIClient()

    def authenticate_as_user(self):
        self.client.force_authenticate(self.user)

    def authenticate_as_admin(self):
        self.client.force_authenticate(self.admin)

    def test_user_can_update_own_profile(self):
        self.authenticate_as_user()
        data = {"first_name": "John", "last_name": "Doe", "email": "john@example.com"}
        response = self.client.patch(f"/users/{self.user.id}/", data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertEqual(self.user.first_name, "John")
        self.assertEqual(self.user.email, "john@example.com")

    def test_user_cannot_update_other_user(self):
        self.authenticate_as_user()
        data = {"first_name": "Hacker"}
        response = self.client.patch(f"/users/{self.other_user.id}/", data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_admin_can_update_any_user(self):
        self.authenticate_as_admin()
        data = {"first_name": "AdminUpdated"}
        response = self.client.patch(f"/users/{self.user.id}/", data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertEqual(self.user.first_name, "AdminUpdated")