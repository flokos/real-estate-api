from rest_framework.test import APIClient
from django.test import TestCase
from ..models import User

class AuthTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="user",
            email="test@example.com",
            password="StrongPass123!",
            first_name="Test",
            last_name="User"
        )
        self.unauthenticated_client = APIClient()

    def test_jwt_token_generation(self):
        response = self.unauthenticated_client.post("/auth/token/", {"username": self.user.username, "password": "invalid"}, format="json")
        self.assertEqual(response.status_code, 401)  # invalid password
        # Create a real password & try again
        self.user.set_password("StrongPass123!")
        self.user.save()
        response = self.unauthenticated_client.post("/auth/token/", {"username": self.user.username, "password": "StrongPass123!"}, format="json")
        self.assertEqual(response.status_code, 200)
        self.assertIn("access", response.data)

    def test_requires_authentication(self):
        response = self.unauthenticated_client.get("/transactions/")
        self.assertEqual(response.status_code, 401)