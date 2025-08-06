from ...models import Property, Transaction, User
from django.utils.timezone import now
from django.test import TestCase
from django.core.management import call_command
from rest_framework.test import APIClient

class TransactionDetailTests(TestCase):
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
        self.property = Property.objects.create(title="DetailProp", district="Limassol", estimated_value=100000, user=self.user)
        self.txn = Transaction.objects.create(user=self.user, property=self.property, percentage=20, price=50000, transaction_date=now())

    def test_get_transaction_detail(self):
        response = self.client.get(f"/transactions/{self.txn.id}/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['id'], self.txn.id)