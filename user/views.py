from rest_framework import generics, permissions, viewsets
from rest_framework.generics import (
    RetrieveAPIView,
    UpdateAPIView,
    DestroyAPIView)

from user.models import User
from user.permissions import IsAdmin
from user.serializers import UserSerializer


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
