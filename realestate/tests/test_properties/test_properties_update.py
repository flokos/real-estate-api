from rest_framework import status
from ...models import Property, Transaction, User
from django.utils.timezone import now
from django.test import TestCase
from rest_framework.test import APIClient
from django.core.management import call_command
class PropertyUpdateTests(TestCase):

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

    def test_update_property(self):

        update_data = {"title": "Updated Beach House"}
        response = self.client.patch(f"/properties/{self.property.id}/", update_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.property.refresh_from_db()
        self.assertEqual(self.property.title, update_data['title'])

    def test_cannot_update_estimated_value_that_breaks_transactions(self):
        # Create a transaction: price = 100,000 on a 500,000 property
        Transaction.objects.create(
            user=self.user,
            property=self.property,
            percentage=20,
            price=100000,
            transaction_date=now()
        )
        # Try to reduce estimated_value so 100k becomes >150% of new value
        response = self.client.patch(
            f"/properties/{self.property.id}/",
            {"estimated_value": 50000},  # 100k now = 200% of new value
            format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("estimated_value", response.data)