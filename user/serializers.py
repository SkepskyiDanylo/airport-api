from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from user.models import User


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = (
            "id",
            "email",
            "password",
            "is_staff",
            "is_superuser",
        )
        extra_kwargs = {
            "password": {
                "write_only": True,
                "style": {"input_type": "password"},
            }
        }
        read_only_fields = ("id", "is_staff", "is_superuser")

    def validate_password(self, value):
        try:
            validate_password(value)
        except DjangoValidationError as e:
            raise ValidationError(e.messages)
        return value

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user

    def update(self, instance, validated_data):
        password = validated_data.pop("password", None)
        for field, value in validated_data.items():
            setattr(instance, field, value)
        if password:
            instance.set_password(password)
        instance.save()
        return instance
