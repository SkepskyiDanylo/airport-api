import uuid
from decimal import Decimal, ROUND_DOWN, InvalidOperation

from django.contrib.auth import get_user, get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.db import transaction
from django.http import HttpResponseRedirect
from django.utils.translation import gettext as _
from rest_framework import generics, permissions, viewsets, status
from rest_framework.generics import (
    RetrieveAPIView,
    UpdateAPIView,
    DestroyAPIView, get_object_or_404
)
from rest_framework.response import Response
from rest_framework.views import APIView
import stripe

from airport_api import settings
from user.models import User, Transaction
from user.permissions import IsAdmin
from user.serializers import (
    UserSerializer,
    RequestPasswordResetSerializer,
    SetNewPasswordSerializer,
    EmptySerializer
)

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

    def perform_create(self, serializer):
        user = serializer.save()
        uid = str(user.id)
        token = default_token_generator.make_token(user)
        link = f"{settings.FRONTEND_URL}/email-activate/{uid}/{token}/"
        send_mail(
            "Activate your account",
            f"Please activate your account: {link}",
            settings.DEFAULT_FROM_EMAIL,
            [user.email]
        )


class ActivateAccountView(generics.RetrieveAPIView):
    serializer_class = EmptySerializer

    def get(self, request, uid = None, token = None):
        try:
            uid = uuid.UUID(uid)
            user = User.objects.get(pk=uid)
        except Exception:
            return HttpResponseRedirect({"detail": _("Invalid link")}, status=status.HTTP_400_BAD_REQUEST)

        if default_token_generator.check_token(user, token):
            user.is_active = True
            user.save()
            return Response({"detail": _("Account activated")}, status=status.HTTP_200_OK)
        return Response({"detail": _("Token invalid or expired")}, status=status.HTTP_400_BAD_REQUEST)


class PasswordResetView(generics.GenericAPIView):
    serializer_class = RequestPasswordResetSerializer


    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data["email"]
        user = get_object_or_404(get_user_model(), email=email)
        if user:
            uid = str(user.id)
            token = default_token_generator.make_token(user)
            link = f"{settings.FRONTEND_URL}/reset-password-confirm/{uid}/{token}/"
            send_mail(
                "Reset your password",
                f"Use this link to reset your password: {link}",
                settings.DEFAULT_FROM_EMAIL,
                [email]
            )
        return Response({"detail": _("If email is registered, a reset link has been sent")}, status=status.HTTP_200_OK)


class CheckPasswordTokenView(generics.RetrieveAPIView):

    def get(self, request, uid = None, token = None):
        try:
            uid = uuid.UUID(uid)
            user = User.objects.get(pk=uid)
        except (get_user_model().DoesNotExist, ValueError):
            return Response({"valid": False, "detail": _("Invalid link")}, status=status.HTTP_400_BAD_REQUEST)

        valid = default_token_generator.check_token(user, token)
        return Response({"valid": valid}, status=status.HTTP_200_OK if valid else status.HTTP_400_BAD_REQUEST)


class SetNewPasswordAPIView(generics.GenericAPIView):
    serializer_class = SetNewPasswordSerializer

    def patch(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        uid = serializer.validated_data["uid"]
        token = serializer.validated_data["token"]
        password = serializer.validated_data["password"]

        try:
            user = User.objects.get(pk=uid)
        except User.DoesNotExist:
            return Response({"detail": _("Invalid uid")}, status=status.HTTP_400_BAD_REQUEST)

        if not default_token_generator.check_token(user, token):
            return Response({"detail": _("Token invalid or expired")}, status=status.HTTP_400_BAD_REQUEST)

        user.set_password(password)
        user.save()
        return Response({"detail": _("Password reset successful")}, status=status.HTTP_200_OK)


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
            # logging
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
                transaction_amount = (Decimal(amount_paid_cents) / Decimal("100")).quantize(Decimal("0.01"), rounding=ROUND_DOWN)
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
            return Response({"detail": _("Stripe error")}, status=status.HTTP_503_SERVICE_UNAVAILABLE)
