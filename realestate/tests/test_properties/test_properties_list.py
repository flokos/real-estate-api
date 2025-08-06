from rest_framework import status
from ...models import Property, User
from django.test import TestCase
from rest_framework.test import APIClient
from django.core.management import call_command
class PropertyListTests(TestCase):

    def setUp(self):
        call_command('flush', '--noinput')
        self.client = APIClient()
        self.user = User.objects.create_user(
            username="user",
            email="test@example.com",
            password="StrongPass123!",
            first_name="Test",
            last_name="User"
        )
        print(f"User from base api test case: {self.user.id}")
        self.client.force_authenticate(user=self.user)
        self.property_data = {
            "title": "Beach House",
            "district": "Limassol",
            "estimated_value": 500000,
            "user": self.user,
        }
        self.property = Property.objects.create(**self.property_data)

    def test_list_properties(self):
        
        Property.objects.create(title="Mountain Villa", district="Nicosia", estimated_value=750000, user=self.user)
        response = self.client.get("/properties/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data), 1)  # At least one property
        self.assertIn("title", response.data[0])