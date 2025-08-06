from rest_framework import status
from rest_framework.test import APIClient
from django.core.management import call_command
from ...models import User
from django.test import TestCase

class UsersCreateTests(TestCase):
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

    def test_admin_can_delete_user(self):
        self.authenticate_as_admin()
        response = self.client.delete(f"/users/{self.other_user.id}/")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(User.objects.filter(id=self.other_user.id).exists())

    def test_user_cannot_delete_user(self):
        self.authenticate_as_user()
        response = self.client.delete(f"/users/{self.other_user.id}/")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)