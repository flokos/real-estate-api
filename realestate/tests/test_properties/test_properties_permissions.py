from rest_framework import status
from ...models import Property, User
from django.test import TestCase
from rest_framework.test import APIClient
from django.core.management import call_command
class PropertyPermissionsTests(TestCase):
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
        self.admin = User.objects.create_user(
            username="admin",
            email="admin@example.com",
            password="AdminPass123!",
            is_staff=True
        )
        self.property = Property.objects.create(
            title="Beach House",
            district="Limassol",
            estimated_value=500000,
            user=self.user
        )

    def test_user_can_list_properties(self):
        response = self.client.get("/properties/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_user_can_retrieve_property(self):
        response = self.client.get(f"/properties/{self.property.id}/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["id"], self.property.id)

    def test_user_cannot_update_other_users_property(self):
        other_user = User.objects.create_user(username="other", email="other@example.com", password="pass1234")
        other_property = Property.objects.create(
            title="Other's House",
            district="Nicosia",
            estimated_value=300000,
            user=other_user
        )
        response = self.client.patch(f"/properties/{other_property.id}/", {"title": "Hacked"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_user_can_update_own_property(self):
        response = self.client.patch(f"/properties/{self.property.id}/", {"title": "Updated Beach House"},
                                     format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.property.refresh_from_db()
        self.assertEqual(self.property.title, "Updated Beach House")

    def test_user_cannot_delete_other_users_property(self):
        other_user = User.objects.create_user(username="other", email="other@example.com", password="pass1234")
        other_property = Property.objects.create(
            title="Other's House",
            district="Nicosia",
            estimated_value=300000,
            user=other_user
        )
        response = self.client.delete(f"/properties/{other_property.id}/")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_user_cannot_create_property_for_other_user(self):
        other_user = User.objects.create_user(username="other", email="other@example.com", password="pass1234")
        data = {
            "title": "Fake Owner House",
            "district": "Nicosia",
            "estimated_value": 400000,
            "user": other_user.id
        }
        response = self.client.post("/properties/", data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["user"], self.user.id)  # Overridden
