from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView
)

from user.views import UserRegister, UserViewSet, MyProfileView

router = DefaultRouter()
router.register("users", UserViewSet, basename="user")

urlpatterns = [
    path("token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("token/verify/", TokenVerifyView.as_view(), name="token_verify"),
    path("register/", UserRegister.as_view(), name="register"),
    path("me/", MyProfileView.as_view(), name="my-profile"),
    path("", include(router.urls)),
]


app_name = "user"
