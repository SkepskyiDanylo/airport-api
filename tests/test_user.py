from decimal import Decimal
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.core import mail
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APITestCase

from airport_api import settings
from user.models import Transaction

EMAIL = "test@test.com"
PASSWORD = "test_password"
USER_MODEL = get_user_model()

def sample_user():
    return USER_MODEL.objects.create_user(
        email=EMAIL,
        password=PASSWORD,
    )

class TestUnauthenticatedUser(APITestCase):
    REGISTER_URL = reverse("user:register")
    TOKEN_URL = reverse("user:token_obtain_pair")
    REFRESH_URL = reverse("user:token_refresh")
    TOKEN_VERIFY_URL = reverse("user:token_verify")


    def test_register(self):
        payload = {
            "email": EMAIL,
            "password": PASSWORD
        }
        res = self.client.post(
            self.REGISTER_URL,
            data=payload
        )
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(USER_MODEL.objects.count(), 1)
        if settings.USE_EMAIL_VERIFICATION:
            self.assertEqual(len(mail.outbox), 1)
            email = mail.outbox[0]
            self.assertEqual(email.subject, "Activate your account")
            self.assertEqual(email.to, [EMAIL])

    def test_token(self):
        sample_user()
        payload = {
            "email": EMAIL,
            "password": PASSWORD
        }
        res = self.client.post(
            self.TOKEN_URL,
            data=payload
        )
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_token_refresh(self):
        sample_user()
        payload = {
            "email": EMAIL,
            "password": PASSWORD
        }
        res = self.client.post(
            self.TOKEN_URL,
            data=payload
        )
        refresh = res.data.get("refresh", "")
        payload = {
            "refresh": refresh,
        }
        res = self.client.post(
            self.REFRESH_URL,
            data=payload
        )
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertContains(res, "access")

    def test_token_verify(self):
        sample_user()
        payload = {
            "email": EMAIL,
            "password": PASSWORD
        }
        res = self.client.post(
            self.TOKEN_URL,
            data=payload
        )
        access = res.data["access"]
        payload = {
            "token": access,
        }
        res = self.client.post(
            self.TOKEN_VERIFY_URL,
            data=payload
        )
        self.assertEqual(res.status_code, status.HTTP_200_OK)


class TestAuthenticatedUser(APITestCase):

    def setUp(self):
        self.user = sample_user()
        self.client.force_authenticate(user=self.user)

    def test_my_profile(self):
        url = reverse("user:my-profile")
        res = self.client.get(url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertContains(res, EMAIL)
        self.assertNotContains(res, PASSWORD)

    def test_deposit(self):
        url = reverse("user:stripe-deposit")
        payload = {
            "amount": 100,
        }
        res = self.client.post(
            url,
            data=payload
        )
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertContains(res, "url")

    @patch("stripe.Webhook.construct_event")
    def test_stripe_webhook_checkout_session_completed(self, mock_construct_event):
        url = reverse("user:stripe-webhook")  # Убедись, что это правильное имя URL

        stripe_event = {
            "type": "checkout.session.completed",
            "data": {
                "object": {
                    "amount_total": 5500,
                    "customer_details": {"email": self.user.email},
                    "metadata": {"user_id": str(self.user.id)},
                }
            }
        }
        mock_construct_event.return_value = stripe_event

        response = self.client.post(
            url,
            data=stripe_event,
            format="json",
            HTTP_STRIPE_SIGNATURE="fake-signature"
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.user.refresh_from_db()
        self.assertEqual(self.user.balance, Decimal("55.00"))

        transaction = Transaction.objects.get(user=self.user)
        self.assertEqual(transaction.amount, Decimal("55.00"))
        self.assertEqual(transaction.status, "SUCCESS")
        self.assertEqual(transaction.email, self.user.email)

    @patch("stripe.Webhook.construct_event")
    def test_stripe_webhook_async_payment_failed(self, mock_construct_event):
        url = reverse("user:stripe-webhook")

        stripe_event = {
            "type": "checkout.session.async_payment_failed",
            "data": {
                "object": {
                    "customer_details": {"email": self.user.email},
                    "metadata": {
                        "user_id": str(self.user.id),
                        "amount": "4200"
                    }
                }
            }
        }

        mock_construct_event.return_value = stripe_event

        response = self.client.post(
            url,
            data=stripe_event,
            format="json",
            HTTP_STRIPE_SIGNATURE="fake-signature"
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        transaction = Transaction.objects.get(user=self.user)
        self.assertEqual(transaction.amount, Decimal("42.00"))
        self.assertEqual(transaction.status, "FAILED")
        self.assertEqual(transaction.email, self.user.email)
