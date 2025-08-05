import uuid

from django.contrib.auth.models import (
    AbstractUser,
    BaseUserManager,
)
from django.core.validators import MinValueValidator
from django.db import models
from django.utils.translation import gettext_lazy as _


# noinspection PySimplifyBooleanCheck
class UserManager(BaseUserManager):
    """Define a model manager for User model with no username field."""

    use_in_migrations = True

    def _create_user(self, email, password, **extra_fields):
        """Create and save a User with the given email and password."""
        if not email:
            raise ValueError("The given email must be set")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        """Create and save a regular User with the given email and password."""
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        """Create and save a SuperUser with the given email and password."""
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self._create_user(email, password, **extra_fields)


class User(AbstractUser):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    username = None
    email = models.EmailField(_("Email address."), unique=True)
    balance = models.DecimalField(
        _("Balance in dollars."),
        max_digits=10,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0)],
    )

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    objects = UserManager()

    def __str__(self):
        return self.email


class Transaction(models.Model):
    STATUS_CHOICES = (
        ("SUCCESS", _("Success")),
        ("FAILURE", _("Failure")),
    )
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    email = models.EmailField()
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
    )

    class Meta:
        ordering = ["-date"]
        verbose_name_plural = _("Transactions")
        verbose_name = _("Transaction")

    def __str__(self):
        return f"{self.amount} {self.status}"
