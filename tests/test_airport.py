from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APITestCase

from airport.models import AirplaneType
from tests.test_user import sample_user

class TestPermissions(APITestCase):

    def setUp(self):
        self.user = sample_user()
        self.admin = sample_user(email="admin@admin.com", is_staff=True, is_superuser=True)
        self.airplane_type = AirplaneType.objects.create(name="Airplane")
        self.list_url = reverse("airport:airplane-type-list")
        self.detail_url = reverse("airport:airplane-type-detail", kwargs={"pk": self.airplane_type.id})
        self.payload = {
            "name": "Test"
        }

    def test_unauthorized(self):
        res = self.client.get(self.list_url)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)
        res = self.client.post(self.list_url, data=self.payload)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)
        res = self.client.get(self.detail_url)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)
        res = self.client.patch(self.detail_url, data=self.payload)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)
        res = self.client.put(self.detail_url, data=self.payload)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_authorized(self):
        self.client.force_authenticate(self.user)
        res = self.client.get(self.list_url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        res = self.client.post(self.list_url, data=self.payload)
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)
        res = self.client.get(self.detail_url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        res = self.client.patch(self.detail_url, data=self.payload)
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)
        res = self.client.put(self.detail_url, data=self.payload)
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_admin(self):
        self.client.force_authenticate(self.admin)
        res = self.client.get(self.list_url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        res = self.client.post(self.list_url, data=self.payload)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        res = self.client.get(self.detail_url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        res = self.client.patch(self.detail_url, data=self.payload)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        res = self.client.put(self.detail_url, data=self.payload)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
