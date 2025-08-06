from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView
)

from airport_api import settings
from user.views import (
    UserRegister,
    UserViewSet,
    MyProfileView,
    UserDeposit,
    StripeWebhookView,
    ActivateAccountView,
    PasswordResetView,
    CheckPasswordTokenView,
    SetNewPasswordAPIView,
)

router = DefaultRouter()
router.register("users", UserViewSet, basename="user")

urlpatterns = [
    path("token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("token/verify/", TokenVerifyView.as_view(), name="token_verify"),
    path("register/", UserRegister.as_view(), name="register"),
    path("me/", MyProfileView.as_view(), name="my-profile"),
    path("deposit/", UserDeposit.as_view(), name="stripe-deposit"),
    path("deposit/webhook/", StripeWebhookView.as_view(), name="stripe-webhook"),
    path("", include(router.urls)),
]


if settings.USE_EMAIL_VERIFICATION:
    urlpatterns += [
        path(
            "activate/<str:uid>/<str:token>/", ActivateAccountView.as_view(), name="email-activate"
        ),
        path("password/reset/", PasswordResetView.as_view(), name="password-reset"),
        path(
            "password/check/<str:uid>/<str:token>/",
            CheckPasswordTokenView.as_view(),
            name="password-check"
        ),
        path("password/set/", SetNewPasswordAPIView.as_view(), name="password-set"),
    ]


app_name = "user"
