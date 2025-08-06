from rest_framework import status
from django.utils.timezone import now
from ...models import Property, Transaction, User
from rest_framework.test import APIClient
from django.test import TestCase
from django.core.management import call_command

class TransactionCreateTests(TestCase):
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
        self.property = Property.objects.create(
            title="Test Property",
            district="Limassol",
            estimated_value=500000,
            user=self.user,
        )
        Transaction.objects.create(
            user=self.user,
            property=self.property,
            percentage=60,
            price=350000,
            transaction_date=now()
        )

    def test_create_transaction_success(self):
        data = {
            "user": self.user.id,
            "property": self.property.id,
            "percentage": 20,
            "price": 300000,
            "transaction_date": now().isoformat()
        }
        response = self.client.post("/transactions/", data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Transaction.objects.count(), 2)
        created_tx_id = response.data['id']
        created_tx = Transaction.objects.get(id=created_tx_id)
        self.assertEqual(created_tx.percentage, data["percentage"])
        self.assertEqual(created_tx.price, data["price"])
        self.assertEqual(created_tx.user.id, data["user"])

    def test_create_transaction_exceeds_total_ownership(self):
        print("Actual test user:", self.user.id)

        data = {
            "user": self.user.id,
            "property": self.property.id,
            "percentage": 50,
            "price": 200000,
            "transaction_date": now().isoformat()
        }
        response = self.client.post("/transactions/", data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("percentage", response.data)

    def test_create_transaction_user_owns_more_than_80_percent(self):

        data = {
            "user": self.user.id,
            "property": self.property.id,
            "percentage": 30,  # 60 + 30 = 90%
            "price": 350000,
            "transaction_date": now().isoformat()
        }
        response = self.client.post("/transactions/", data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("percentage", response.data)

    def test_create_transaction_below_minimum_investment(self):

        data = {
            "user": self.user.id,
            "property": self.property.id,
            "percentage": 5,
            "price": 5000,
            "transaction_date": now().isoformat()
        }
        response = self.client.post("/transactions/", data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("price", response.data)

    def test_create_transaction_price_outside_reasonable_range(self):

        data = {
            "user": self.user.id,
            "property": self.property.id,
            "percentage": 10,
            "price": 200000,
            "transaction_date": now().isoformat()
        }
        response = self.client.post("/transactions/", data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("price", response.data)

    def test_create_transaction_missing_user(self):

        data = {
            "property": self.property.id,
            "percentage": 10,
            "price": 350000,
            "transaction_date": now().isoformat()
        }
        response = self.client.post("/transactions/", data, format="json")
        print(response.data)
        # It should be succesful because even if user is missing in the payload it is overriden in the view with the current user.
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn("user", response.data)

    def test_create_transaction_missing_property(self):

        data = {
            "user": self.user.id,
            "percentage": 10,
            "price": 50000,
            "transaction_date": now().isoformat()
        }
        response = self.client.post("/transactions/", data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("property", response.data)

    def test_create_transaction_missing_percentage(self):

        data = {
            "user": self.user.id,
            "property": self.property.id,
            "price": 50000,
            "transaction_date": now().isoformat()
        }
        response = self.client.post("/transactions/", data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("percentage", response.data)

    def test_create_transaction_missing_price(self):

        data = {
            "user": self.user.id,
            "property": self.property.id,
            "percentage": 10,
            "transaction_date": now().isoformat()
        }
        response = self.client.post("/transactions/", data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("price", response.data)

    def test_create_transaction_missing_transaction_date(self):

        data = {
            "user": self.user.id,
            "property": self.property.id,
            "percentage": 10,
            "price": 50000
        }
        response = self.client.post("/transactions/", data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("transaction_date", response.data)