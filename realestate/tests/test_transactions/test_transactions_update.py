from django.core.management import call_command
from django.utils.timezone import now
from rest_framework import status
from rest_framework.test import APIClient
from django.test import TestCase
from ...models import Property, Transaction, User


class TransactionUpdateTests(TestCase):
    def setUp(self):
        call_command('flush', '--noinput')
        self.client = APIClient()
        self.user = User.objects.create_user(username="user", email="test@example.com", password="StrongPass123!",
            first_name="Test", last_name="User")
        self.client.force_authenticate(user=self.user)
        self.property = Property.objects.create(title="Test Property", district="Limassol", estimated_value=500000, user=self.user)
        self.new_property = Property.objects.create(
            title="Another Property",
            district="Nicosia",
            estimated_value=300000,
            user=self.user
        )
        self.transaction = Transaction.objects.create(user=self.user, property=self.property, percentage=50,
            price=350000, transaction_date=now())
        self.update_url = f"/transactions/{self.transaction.id}/"
    def test_update_transaction(self):
        data = {"percentage": 30, "price": 350000}
        response = self.client.patch(self.update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.transaction.refresh_from_db()
        self.assertEqual(self.transaction.percentage, data["percentage"])
        self.assertEqual(self.transaction.price, data["price"])

    def test_update_transaction_exceeds_total_ownership(self):
        data = {"percentage": 120}  # Over 100%
        response = self.client.patch(self.update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("percentage", response.data)

    def test_update_transaction_exceeds_user_ownership(self):
        data = {
            "percentage": 90,
        }
        response = self.client.patch(self.update_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("percentage", response.data)

    def test_user_cannot_update_property_of_transaction(self):

        data = {
            "property": self.new_property.id,
        }
        response = self.client.patch(self.update_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("property", response.data)