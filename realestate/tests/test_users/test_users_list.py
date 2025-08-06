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
        self.client.force_authenticate(self.user)

    def test_user_can_list_all_users(self):
        response = self.client.get("/users/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data), 2)

    def test_user_can_retrieve_any_user(self):
        response = self.client.get(f"/users/{self.other_user.id}/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["id"], self.other_user.id)