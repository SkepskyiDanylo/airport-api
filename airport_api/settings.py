import os
from datetime import timedelta
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent


SECRET_KEY = os.getenv("SECRET_KEY")
DEBUG = os.getenv("DEBUG").lower() == "true"

# Stripe
STRIPE_API_KEY = os.getenv("STRIPE_API_KEY")
STRIPE_WEBHOOK_SECRET = os.getenv("STRIPE_WEBHOOK_SECRET")
SUCCESS_URL = os.getenv("SUCCESS_URL")
CANCEL_URL = os.getenv("CANCEL_URL")

# SMTP
USE_EMAIL_VERIFICATION = os.getenv("USE_EMAIL_VERIFICATION").lower() == "true"
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = os.getenv("SMTP_HOST")
EMAIL_PORT = os.getenv("SMTP_PORT")
EMAIL_USE_TLS = True
EMAIL_HOST_USER = os.getenv("SMTP_HOST_USER")
EMAIL_HOST_PASSWORD = os.getenv("SMTP_PASSWORD")
DEFAULT_FROM_EMAIL = os.getenv("SMTP_DEFAULT_FROM_EMAIL")
FRONTEND_URL = os.getenv("FRONTEND_URL")

ALLOWED_HOSTS = []


INTERNAL_IPS = [
    "127.0.0.1",
    "localhost",
]


INSTALLED_APPS = [
    "jazzmin",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "debug_toolbar",
    "rest_framework",
    "rest_framework_simplejwt",
    "drf_spectacular",
    "airport",
    "user",
]


MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "debug_toolbar.middleware.DebugToolbarMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "airport_api.urls"


WSGI_APPLICATION = "airport_api.wsgi.application"


DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]


SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=60),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=30),
    "ROTATE_REFRESH_TOKENS": False,
    "BLACKLIST_AFTER_ROTATION": True,
    "UPDATE_LAST_LOGIN": True,
}


REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework_simplejwt.authentication.JWTAuthentication",
        "rest_framework.authentication.BasicAuthentication",
    ],
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
    "DEFAULT_THROTTLE_CLASSES": [
        "rest_framework.throttling.ScopedRateThrottle",
        "rest_framework.throttling.UserRateThrottle",
    ],
    "DEFAULT_THROTTLE_RATES": {
        "login": "10/minute",
        "user": "200/minute",
        "refresh": "100/minute",
    },
}


TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]


LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_TZ = True


STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "static"

MEDIA_ROOT = BASE_DIR / "media"
MEDIA_URL = "/media/"

AUTH_USER_MODEL = "user.User"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

JAZZMIN_UI_TWEAKS = {
    "navbar_small_text": False,
    "footer_small_text": False,
    "body_small_text": False,
    "brand_small_text": False,
    "brand_colour": False,
    "accent": "accent-primary",
    "navbar": "navbar-dark",
    "no_navbar_border": True,
    "navbar_fixed": False,
    "layout_boxed": False,
    "footer_fixed": False,
    "sidebar_fixed": False,
    "sidebar": "sidebar-dark-navy",
    "sidebar_nav_small_text": False,
    "sidebar_disable_expand": False,
    "sidebar_nav_child_indent": False,
    "sidebar_nav_compact_style": False,
    "sidebar_nav_legacy_style": False,
    "sidebar_nav_flat_style": True,
    "theme": "darkly",
    "dark_mode_theme": "solar",
    "button_classes": {
        "primary": "btn-primary",
        "secondary": "btn-secondary",
        "info": "btn-info",
        "warning": "btn-warning",
        "danger": "btn-danger",
        "success": "btn-success"
    },
    "actions_sticky_top": False
}

JAZZMIN_SETTINGS = {
    "site_title": "aiorport-api",
    "site_header": "Airport API",
    "site_brand": "airport-api",
    "welcome_sign": "Welcome to airport admin panel",
    "topmenu_links": [
        {"name": "Swagger", "url": "/swagger/"},
    ],
    "show_sidebar": True,
    "changeform_format": "single",
    "related_modal_active": True,
    "icons": {
        "user.User": "fa-solid fa-user",
        "user.Transaction": "fa-solid fa-credit-card",
        "airport.AirplaneType": "fa-solid fa-plane-circle-check",
        "airport.Airplane": "fa-solid fa-plane",
        "airport.Crew": "fa-solid fa-id-card-clip",
        "airport.Airport": "fa-solid fa-plane-arrival",
        "airport.Route": "fa-solid fa-route",
        "airport.Flight": "fa-solid fa-plane-departure",
        "airport.Order": "fa-solid fa-money-check",
        "airport.Ticket": "fa-solid fa-ticket",
    }
}

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "{levelname} {asctime} {module} {message}",
            "style": "{",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "verbose",
        },
    },
    "root": {
        "handlers": ["console"],
        "level": "WARNING",
    },
}


SPECTACULAR_SETTINGS = {
    "TITLE": "Swagger",
    "DESCRIPTION": "AIRPORT internal api",
    "VERSION": "1.0.0",
    "SECURITY_SCHEMES": {
        "BasicAuth": {
            "type": "http",
            "scheme": "basic"
        },
        "BearerAuth": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT"
        }
    },
    "DEFAULT_SECURITY": [
        {"BasicAuth": []},
        {"BearerAuth": []}
    ],
    "filter": True,
    "SWAGGER_UI_SETTINGS": {
        "deepLinking": True,
    },
    "COMPONENT_SPLIT_REQUEST": True
}
