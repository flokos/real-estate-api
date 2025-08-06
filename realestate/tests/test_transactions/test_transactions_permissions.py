from django.utils.timezone import now
from ...models import Property, Transaction, User
from django.test import TestCase
from django.core.management import call_command
from rest_framework.test import APIClient
from rest_framework import status

class TransactionPermissionsTests(TestCase):
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
        self.admin = User.objects.create_user(
            username="admin",
            email="admin@example.com",
            password="AdminPass123!",
            is_staff=True
        )
        self.other_user = User.objects.create_user(username="other_user", email="other@example.com", password="pass1234")
        self.property = Property.objects.create(
            title="Test Property",
            district="Limassol",
            estimated_value=500000,
            user=self.user
        )
        self.transaction = Transaction.objects.create(
            user=self.user,
            property=self.property,
            percentage=20,
            price=350000,
            transaction_date=now()
        )
        self.other_transaction = Transaction.objects.create(
            user=self.other_user,
            property=self.property,
            percentage=10,
            price=340000,
            transaction_date=now()
        )

    def test_user_can_list_transactions(self):
        response = self.client.get("/transactions/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_user_can_retrieve_transaction(self):
        response = self.client.get(f"/transactions/{self.transaction.id}/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["id"], self.transaction.id)

    def test_user_cannot_update_other_users_transaction(self):
        response = self.client.patch(f"/transactions/{self.other_transaction.id}/", {"percentage": 30}, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_user_can_update_own_transaction(self):
        response = self.client.patch(f"/transactions/{self.transaction.id}/", {"percentage": 25}, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.transaction.refresh_from_db()
        self.assertEqual(self.transaction.percentage, 25)

    def test_user_cannot_delete_other_users_transaction(self):
        response = self.client.delete(f"/transactions/{self.other_transaction.id}/")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_user_cannot_create_transaction_for_other_user(self):
        data = {
            "property": self.property.id,
            "percentage": 15,
            "price": 375000,
            "transaction_date": now().isoformat(),
            "user": self.other_user.id
        }
        response = self.client.post("/transactions/", data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["user"], self.user.id)  # Overridden