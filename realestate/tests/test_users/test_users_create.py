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

    def test_admin_can_create_user(self):
        self.authenticate_as_admin()
        data = {"username": "newuser", "password": "pass123"}
        response = self.client.post("/users/", data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(User.objects.filter(username="newuser").exists())

    def test_user_cannot_create_user(self):
        self.authenticate_as_user()
        data = {"username": "unauthorized", "password": "pass123"}
        response = self.client.post("/users/", data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

