from django.test import TestCase
from rest_framework.test import APIClient
from ...models import User
from rest_framework import status
from django.core.management import call_command

class PropertyCreateTests(TestCase):

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

    def test_create_property(self):

        data = {
            "title": "Mountain Villa",
            "district": "Nicosia",
            "estimated_value": 750000
        }
        response = self.client.post("/properties/", data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['title'], data['title'])

    def test_create_property_invalid_district(self):

        data = {
            "title": "Bad District Property",
            "district": "InvalidDistrict",
            "estimated_value": 400000
        }
        response = self.client.post("/properties/", data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("district", response.data)

    def test_create_property_missing_title(self):
        data = {
            "district": "Nicosia",
            "estimated_value": 750000
        }
        response = self.client.post("/properties/", data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("title", response.data)

    def test_create_property_missing_district(self):
        data = {
            "title": "Property Without District",
            "estimated_value": 750000
        }
        response = self.client.post("/properties/", data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("district", response.data)

    def test_create_property_missing_estimated_value(self):
        data = {
            "title": "Property Without Value",
            "district": "Nicosia"
        }
        response = self.client.post("/properties/", data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("estimated_value", response.data)