from rest_framework import status
from django.utils.timezone import now
from ...models import Property, Transaction, User
from rest_framework.test import APIClient
from django.test import TestCase
from django.core.management import call_command

class TransactionDeleteTests(TestCase):
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
        self.client.force_authenticate(user=self.user)
        self.property = Property.objects.create(title="Test Property", district="Limassol", estimated_value=500000, user=self.user)
        self.transaction = Transaction.objects.create(
            user=self.user,
            property=self.property,
            percentage=50,
            price=250000,
            transaction_date=now()
        )

    def test_delete_transaction(self):

        response = self.client.delete(f"/transactions/{self.transaction.id}/")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Transaction.objects.count(), 0)