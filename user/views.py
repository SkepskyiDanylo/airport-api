from decimal import Decimal, ROUND_DOWN, InvalidOperation

from django.db import transaction
from django.utils.translation import gettext as _
from rest_framework import generics, permissions, viewsets, status
from rest_framework.generics import (
    RetrieveAPIView,
    UpdateAPIView,
    DestroyAPIView
)
from rest_framework.response import Response
from rest_framework.views import APIView
import stripe

from airport_api import settings
from user.models import User, Transaction
from user.permissions import IsAdmin
from user.serializers import UserSerializer

stripe.api_key = settings.STRIPE_API_KEY
endpoint_secret = settings.STRIPE_WEBHOOK_SECRET


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (IsAdmin,)


class UserRegister(generics.CreateAPIView):
    serializer_class = UserSerializer
    queryset = User.objects.all()
    permission_classes = (permissions.AllowAny,)


class MyProfileView(RetrieveAPIView, UpdateAPIView, DestroyAPIView):
    serializer_class = UserSerializer
    queryset = User.objects.none()
    permission_classes = (permissions.IsAuthenticated,)

    def get_object(self):
        return self.request.user


class StripeWebhookView(APIView):
    authentication_classes = (permissions.AllowAny,)

    def post(self, request, *args, **kwargs):
        payload = request.body
        sig_header = request.META.get("HTTP_STRIPE_SIGNATURE")

        try:
            event = stripe.Webhook.construct_event(
                payload=payload, sig_header=sig_header, secret=endpoint_secret
            )
        except (ValueError, stripe.error.SignatureVerificationError):
            # Needs to add logging of unsuccessful requests
            return Response(status=status.HTTP_400_BAD_REQUEST)

        if event["type"] == "checkout.session.completed":
            session = event["data"]["object"]

            amount_paid_cents = session["amount_total"]
            email = session.get("customer_details", {}).get("email")
            metadata = session.get("metadata", {})
            user_id = metadata.get("user_id")
            try:
                user = User.objects.get(id=user_id)
            except User.DoesNotExist:
                #logging
                return Response(status=status.HTTP_404_NOT_FOUND)
            with transaction.atomic():
                transaction_amount = (Decimal(amount_paid_cents) / Decimal('100')).quantize(Decimal('0.01'), rounding=ROUND_DOWN)
                user.balance += transaction_amount,
                user.save()
                Transaction.objects.create(
                    user=user,
                    amount=transaction_amount,
                    email=email,
                    status="SUCCESS",
                )

        elif event["type"] == "checkout.session.async_payment_failed":
            session = event["data"]["object"]
            email = session.get("customer_details", {}).get("email")
            metadata = session.get("metadata", {})
            user_id = metadata.get("user_id")

            try:
                amount_requested_cents = int(metadata.get("amount", "0"))
            except (ValueError, TypeError):
                amount_requested_cents = 0

            try:
                user = User.objects.get(id=user_id)
            except User.DoesNotExist:
                #logging
                return Response(status=status.HTTP_404_NOT_FOUND)

            with transaction.atomic():
                transaction_amount = (Decimal(amount_requested_cents) / Decimal("100")).quantize(Decimal("0.01"), rounding=ROUND_DOWN)
                Transaction.objects.create(
                    user=user,
                    amount=transaction_amount,
                    email=email,
                    status="FAILED",
                )

        return Response(status=status.HTTP_200_OK)


class UserDeposit(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        try:
            amount = str(request.data.get("amount"))
            amount = Decimal(amount).quantize(Decimal("0.01"), rounding=ROUND_DOWN)
        except (TypeError, ValueError, InvalidOperation):
            return Response({"detail": _("Invalid amount")}, status=status.HTTP_400_BAD_REQUEST)

        if amount < Decimal("0.01"):
            return Response({"detail": _("Amount to low")}, status=status.HTTP_400_BAD_REQUEST)

        try:
            amount_cents = int((amount * 100).to_integral_exact(rounding=ROUND_DOWN))
            session = stripe.checkout.Session.create(
                payment_method_types=["card"],
                line_items=[{
                    "price_data": {
                        "currency": "usd",
                        "product_data": {
                            "name": "Balance deposit",
                        },
                        "unit_amount": amount_cents,
                    },
                    "quantity": 1,
                }],
                mode="payment",
                success_url="http://localhost:8000/success/",
                cancel_url="http://localhost:8000/cancel/",
                metadata={
                    "user_id": self.request.user.id,
                    "amount": str(amount_cents),
                }
            )
            return Response({"url": session.url}, status=status.HTTP_200_OK)
        except stripe.error.StripeError:
            return Response({"detail": "Stripe error"}, status=status.HTTP_503_SERVICE_UNAVAILABLE)
