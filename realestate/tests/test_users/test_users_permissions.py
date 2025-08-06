from rest_framework.test import APIClient
from django.urls import reverse
from django.core.management import call_command
from rest_framework import status
from ...models import User
from django.test import TestCase

class UserPermissionTests(TestCase):
    def setUp(self):
        call_command('flush', '--noinput')
        self.admin = User.objects.create_superuser(username="admin", email="admin@test.com", password="pass")
        self.user1 = User.objects.create_user(username="user1", email="user1@test.com", password="pass")
        self.user2 = User.objects.create_user(username="user2", email="user2@test.com", password="pass")
        self.client = APIClient()

    def test_anonymous_cannot_access_users(self):
        res = self.client.get("/users/")
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_regular_user_cannot_create_user(self):
        self.client.force_authenticate(user=self.user1)
        res = self.client.post("/users/", {"username": "newuser", "password": "pass"})
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_regular_user_can_view_own_profile(self):
        self.client.force_authenticate(user=self.user1)
        res = self.client.get(f"/users/{self.user1.id}/")
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_regular_user_can_view_any_profile(self):
        self.client.force_authenticate(user=self.user1)
        res = self.client.get(f"/users/{self.user2.id}/")
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_regular_user_cannot_update_or_delete_others(self):
        self.client.force_authenticate(user=self.user1)
        res = self.client.patch(f"/users/{self.user2.id}/", {"email": "hack@test.com"})
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

        res = self.client.delete(f"/users/{self.user2.id}/")
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_admin_can_create_update_delete_any_user(self):
        self.client.force_authenticate(user=self.admin)
        # Create
        res = self.client.post("/users/", {"username": "admincreated", "password": "pass"})
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        # Update
        res = self.client.patch(f"/users/{self.user1.id}/", {"email": "newemail@test.com"})
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        # Delete
        res = self.client.delete(f"/users/{self.user2.id}/")
        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)