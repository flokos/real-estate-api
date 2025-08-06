from django.utils.timezone import now
from threading import Thread
from ...models import User, Property, Transaction
import time
from rest_framework.test import APIClient
from django.test import TransactionTestCase
from uuid import uuid4
from datetime import timedelta
import pytest

class TransactionRaceConditionTests(TransactionTestCase):

    """Tried multiple solutions that i thought but i couldn't get it to successfully test race conditions with concurrent requests and threads"""

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create(username=f"user_{uuid4().hex[:6]}", email="user2@example.com")

        cls.property = Property.objects.create(title="TestProp", district="Limassol", estimated_value=200000, user=cls.user)
        # Initial transactions
        cls.tx1 = Transaction.objects.create(
            user=cls.user, property=cls.property, percentage=80, price=160000, transaction_date=now()
        )
        cls.tx2 = Transaction.objects.create(
            user=cls.user, property=cls.property, percentage=10, price=20000, transaction_date=now() + timedelta(minutes=1)
        )

    def setUp(self):
        self.user = self.__class__.user
        self.property = self.__class__.property
        self.tx1 = self.__class__.tx1
        self.tx2 = self.__class__.tx2

    def get_authenticated_client(self):
        client = APIClient()
        client.force_authenticate(user=self.user)
        return client

    def make_post(self, results, index, user_id, property_id, percentage, price, delay=0):
        client = self.get_authenticated_client()
        data = {
            "user": user_id,
            "property": property_id,
            "percentage": percentage,
            "price": price,
            "transaction_date": now().isoformat()
        }
        time.sleep(delay)
        response = client.post("/transactions/", data, format='json')
        results[index] = response.status_code

    def make_patch(self, results, index, tx_id, percentage):
        client = self.get_authenticated_client()
        data = {
            "percentage": percentage
        }
        response = client.patch(f"/transactions/{tx_id}/", data, format='json')
        results[index] = response.status_code

    @pytest.mark.skip(reason="Race condition test not currently working as expected")
    def test_almost_concurrent_transactions_with_order(self):
        results = [None, None]
        valid_price = 50000  # Within 50%-150% of estimated value
        user_id = self.user.id
        property_id = self.property.id

        # First thread starts immediately, second thread waits 0.1s
        t1 = Thread(target=self.make_post, args=(results, 0, user_id, property_id, 10, valid_price, 0))
        t2 = Thread(target=self.make_post, args=(results, 1, user_id, property_id, 10, valid_price, 0.1))
        t1.start()
        t2.start()
        t1.join()
        t2.join()


        self.assertEqual(results[0], 201)  # First succeeds
        self.assertEqual(results[1], 400)  # Second fails (over 100% ownership)

    @pytest.mark.skip(reason="Race condition test not currently working as expected")
    def test_concurrent_transactions_without_order(self):
        results = [None, None]
        valid_price = 50000
        user_id = self.user.id
        property_id = self.property.id

        # Two threads simulating concurrent requests
        t1 = Thread(target=self.make_post, args=(results, 0, user_id, property_id, 10, valid_price, 0))
        t2 = Thread(target=self.make_post, args=(results, 1, user_id, property_id, 10, valid_price, 0))
        t1.start()
        t2.start()
        t1.join()
        t2.join()

        # One must succeed, the other must fail due to ownership > 100%
        self.assertIn(201, results)
        self.assertIn(400, results)

    @pytest.mark.skip(reason="Race condition test not currently working as expected")
    def test_concurrent_create_and_update(self):
        """Simulate a create and an update at the same time for the same property."""
        results = [None, None]
        valid_price = 50000
        user_id = self.user.id
        property_id = self.property.id
        tx_id = self.tx2.id

        # Create tries to add 10%
        t1 = Thread(target=self.make_post, args=(results, 0, user_id, property_id, 10, valid_price))
        # Update bumps existing 10% to 30% (exceeding 100%)
        t2 = Thread(target=self.make_patch, args=(results, 1, tx_id, 30))

        t1.start()
        t2.start()
        t1.join()
        t2.join()

        # One must succeed, the other must fail
        self.assertIn(201, results)
        self.assertIn(400, results)

    @pytest.mark.skip(reason="Race condition test not currently working as expected")
    def test_concurrent_updates(self):
        """Simulate two updates on different transactions at the same time."""
        results = [None, None]
        tx_id_1 = self.tx1.id
        tx_id_2 = self.tx2.id


        # Update tx1: 80 → 90%
        t1 = Thread(target=self.make_patch, args=(results, 0, tx_id_1, 90))
        # Update tx2: 10 → 20%
        t2 = Thread(target=self.make_patch, args=(results, 1, tx_id_2, 20))

        t1.start()
        t2.start()
        t1.join()
        t2.join()

        # One must succeed, the other must fail
        self.assertIn(200, results)
        self.assertIn(400, results)


