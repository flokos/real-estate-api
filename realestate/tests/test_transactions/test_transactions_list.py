from django.utils.timezone import now
from ...models import Property, Transaction, User
from datetime import timedelta
from django.test import TestCase
from django.core.management import call_command
from rest_framework.test import APIClient
from rest_framework import status

class TransactionListTests(TestCase):
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
        self.property1 = Property.objects.create(title="Prop1", district="Limassol", estimated_value=100000, user=self.user)
        self.property2 = Property.objects.create(title="Prop2", district="Nicosia", estimated_value=200000, user=self.user)
        self.tx1 = Transaction.objects.create(user=self.user, property=self.property1, percentage=20, price=50000,
                                   transaction_date=now())
        self.tx2 = Transaction.objects.create(user=self.user, property=self.property2, percentage=30, price=150000,
                                   transaction_date=now() + timedelta(minutes=1))

    def test_list_transactions(self):
        response = self.client.get("/transactions/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
        returned_ids = {t['id'] for t in response.data}
        self.assertIn(self.tx1.id, returned_ids)
        self.assertIn(self.tx2.id, returned_ids)

    def test_filter_by_user(self):
        response = self.client.get(f"/transactions/?user_id={self.user.id}")
        self.assertEqual(len(response.data), 2)

    def test_filter_by_property(self):
        response = self.client.get(f"/transactions/?property_id={self.property1.id}")
        self.assertEqual(len(response.data), 1)

    def test_filter_by_district(self):
        response = self.client.get("/transactions/?district=Limassol")
        self.assertEqual(len(response.data), 1)

    def test_filter_by_price_range(self):
        response = self.client.get("/transactions/?min_price=100000&max_price=200000")
        self.assertEqual(len(response.data), 1)

    def test_filter_by_percentage_range(self):
        response = self.client.get("/transactions/?min_percentage=25&max_percentage=40")
        self.assertEqual(len(response.data), 1)

    def test_filter_by_date_range(self):
        today = now()
        response = self.client.get(f"/transactions/?date_from={today}&date_to={today}")
        self.assertEqual(len(response.data), 2)

    def test_ordering_by_price(self):
        response = self.client.get("/transactions/?ordering=-price")
        self.assertGreater(response.data[1]['price'], response.data[0]['price'])
