from airport_api import settings
from django.test import TestCase


class TestSettings(TestCase):
    REQUIRED_SETTINGS = [
        "SECRET_KEY",
        "DATABASES",
        "INSTALLED_APPS",
        "MIDDLEWARE",
        "ALLOWED_HOSTS",
        "DEBUG",
        "MEDIA_ROOT",
        "MEDIA_URL",
        "STATIC_ROOT",
        "STATIC_URL",
    ]

    REQUIRED_DB_KEYS = [
        "ENGINE",
        "NAME",
        "USER",
        "PASSWORD",
        "HOST",
        "PORT"
    ]

    SMTP_SETTINGS = [
        "EMAIL_BACKEND",
        "EMAIL_HOST",
        "EMAIL_PORT",
        "EMAIL_USE_TLS",
        "EMAIL_HOST_USER",
        "EMAIL_HOST_PASSWORD",
        "DEFAULT_FROM_EMAIL",
    ]

    STRIPE_SETTINGS = [
        "STRIPE_API_KEY",
        "STRIPE_WEBHOOK_SECRET",
        "SUCCESS_URL",
        "CANCEL_URL",
    ]

    def test_required_settings(self):
        for setting in self.REQUIRED_SETTINGS:
            value = getattr(settings, setting, None)
            self.assertIsNotNone(value, f"Setting {setting} should not be None")
            self.assertNotEqual(value, "", f"Setting {setting} should not be empty")

    def test_db_keys(self):
        db_settings = settings.DATABASES.get("default", {})
        self.assertTrue(db_settings, "DATABASES['default'] should exist")

        for key in self.REQUIRED_DB_KEYS:
            value = db_settings.get(key)
            self.assertIsNotNone(value, f"DATABASES['default']['{key}'] should not be None")
            self.assertNotEqual(value, "", f"DATABASES['default']['{key}'] should not be empty")

    def test_smtp_settings(self):
        if settings.USE_EMAIL_VERIFICATION:
            for setting in self.SMTP_SETTINGS:
                value = getattr(settings, setting, None)
                self.assertIsNotNone(value, f"Setting {setting} should not be None")
                self.assertNotEqual(value, "", f"Setting {setting} should not be empty")

    def test_stripe_settings(self):
        for setting in self.STRIPE_SETTINGS:
            value = getattr(settings, setting, None)
            self.assertIsNotNone(value, f"Setting {setting} should not be None")
            self.assertNotEqual(value, "", f"Setting {setting} should not be empty")
