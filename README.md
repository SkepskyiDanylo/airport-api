# ✈️ Airport API

---

## 📑 Table of Contents

- [Overview](#-overview)
- [Environment Variables](#-environment-variables)
- [Simple Installation](#-simple-installation)
- [Docker Installation](#-docker-installation)
- [Project Structure](#-project-structure)
- [API Examples](#-api-examples)
- [API Documentation](#-api-documentation)
- [Translation](#-translation)
- [Email Verification](#-email-verification)
- [Stripe](#-stripe-integration)
- [Contributing](#-contributing)
- [License](#-license)
- [Contact](#-contact)
---

## 🎯 Overview

**Airport API** is a demonstration project built using Django and Django REST Framework that simulates key features of a flight booking system. It includes essential functionalities such as user registration and JWT authentication, flight scheduling, ticket booking, and integration with the Stripe payment system.

The purpose of this project is to showcase my skills and progress in Python backend development, demonstrating how I can build APIs using modern tools and best practices. While its features and architecture are much simpler than those of fully-fledged commercial airline systems, this project lays a solid foundation for future scaling and enhancement.

With additional development and resources, Airport API can be extended into a production-ready application by adding capabilities such as:

- full ticket and boarding pass management,

- integration with external airline systems,

- advanced analytics and reporting,

- more flexible access control and role management,

- support for multiple languages and currencies,

- full-featured flexible email message generation,

- authentication via third-party services (OAuth, social logins),

- integration with accounting systems and invoice generation,

- flexible user profile customization,

- crew availability tracking based on location and working hours,

- and much more.

Therefore, this project not only reflects my current level but also serves as a starting point for creating a real-world product in the air travel domain.

---

## 🚀 Features

- 👤 User registration and authentication  
- 🔐 JWT authentication (SimpleJWT)  
- 🛫 Flight planning and booking  
- 💳 Stripe integration (including Webhooks)  
- ✉️ Email notifications (account activation and password reset)  
- 🧑‍💻 Admin dashboard  
- 📄 Auto-generated API documentation (Swagger & ReDoc)  
- ✅ Tested using Django’s built-in testing tools

---

## 🛠️ Tech Stack

- Python 3.11+
- Django 5.2
- Django REST Framework
- PostgreSQL
- Stripe API
- SimpleJWT
- Swagger / ReDoc
- Django Test Framework

---

## 🔐 Environment Variables

To run this project, you will need to add the following environment variables to your .env file

### Django:

`DEBUG`

`SECRET_KEY`

### Stripe:

`STRIPE_API_KEY` 

`STRIPE_WEBHOOK_SECRET`

`SUCCESS_URL`

`CANCEL_URL`

### SMTP:

`USE_EMAIL_VERIFICATION`

`SMTP_PASSWORD`

`SMTP_HOST`

`SMTP_PORT`

`SMTP_HOST_USER`

`SMTP_DEFAULT_FROM_EMAIL`

`FRONTEND_URL`

### Postgres:

`POSTGRES_PASSWORD`

`POSTGRES_USER`

`POSTGRES_DB`

`POSTGRES_HOST`

`POSTGRES_PORT`

`PGDATA`

Example file with short explanation you can find in *[env.example](env.example)*

---

## ⚙️ Simple Installation

[Fork](https://github.com/SkepskyiDanylo/airport-api/fork) the repository

Create a `.env` file with the [required](#-environment-variables) environment variables

▶️ Install and configure the project:
```bash

git clone https://github.com/your-username/airport-api.git
cd airport-api
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

▶️ Run the Project:

```bash

python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

▶️ (Optional) Load database fixture:
```bash

python manage.py loaddata data.yaml
```

️▶️  To use translation you have to install gettext > 0.25:

1. [Windows](https://github.com/mlocati/gettext-iconv-windows/releases)
2. [Linux](https://www.drupal.org/docs/8/modules/potion/how-to-install-setup-gettext) (Usually preinstalled)

Then run 
```bash

python manage.py compilemessages
```

---

## 🐳 Docker Installation

▶ [Fork](https://github.com/SkepskyiDanylo/airport-api/fork) the repository

Create a `.env` file with the [required](#-environment-variables) environment variables

▶️ Build and start the containers:

```bash

docker-compose build
docker-compose up -d
```

▶️ (Optional) Load database fixture:

```bash

docker exec -it airport-api-airport-1 python manage.py loaddata data.yaml
```

▶️ To stop containers:

```bash

docker-compose down
```
---

## 🧪 Running Tests

```bash

python manage.py test tests
```

---

## 🗄️ Project Structure

```
├── airport/         # Flight planning and booking
├── user/            # User management, Stripe integration, Webhooks
├── tests/           # All tests
├──airport-api/
   ├── settings.py
   └──...
├── .flake8
├── manage.py
├── Dockerfile
├── docker-compose.yaml
└── README.md
```

---

## 🌐 API Examples

### 🔐 Register a New User

```https
POST /api/v1/user/register/
{
  "email": "user@example.com",
  "password": "securepassword123"
}
```

### 🎟 Book a Ticket

```https
POST /api/v1/me/orders/
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJh...
Content-Type: application/json

{
  "tickets": [
    {
      "row": 1,
      "seat": 1,
      "flight": "8e40f430-e1f9-4a37-89d6-f054e1f7f3e3"
    }
  ]
}
```

---

## 📄 API Documentation

You can see all `URIs` by starting the project and using:

- Swagger: [`/swagger/`](http://localhost:8000/swagger/)
- ReDoc: [`/redoc/`](http://localhost:8000/redoc/)

---

## 🔐 Authentication & Access

- JWT-based authentication via `djangorestframework-simplejwt`
- Permissions managed using `IsAuthenticated`, `IsAdmin`, `IsAdminOrAuthenticatedReadOnly` etc.
- Email-based account activation and password reset
- Reworked User model to use `email` instead of `username`
---

## ✉️ Email Verification

To be able to use password reset via email you have to set `USE_EMAIL_VERIFICATION` as `True` in [.env](#-environment-variables)

If `USE_EMAIL_VERIFICATION` is true, after registration email will be sent to user email to activate account.

---

## 🌐 Translation

To add new messages to translation use `gettext` or `gettext_lazy`

1. After adding new messages:
    ```bash
   python manage.py makemessages -l ru
   python manage.py makemessages -l ua
   ```
   Then add translation to messages in `.po` files: [ua](locale/ua/LC_MESSAGES/django.po), [ru](locale/ru/LC_MESSAGES/django.po)
2. To add new language:
    ```bash
   python manage.py makemessages -l language
   ```
   Then add translation to new `.po` file

   Then add new language to [settings.py](airport_api/settings.py)
    ```python
   ...
   LANGUAGES = [
    ("en", "English"),
    ("ru", "Russian"),
    ("ua", "Ukrainian"),
    ("short_code", "Full name") # <- Add your language here
    ]
   ...
   ```
---

## 💳 Stripe Integration

- Stripe Checkout session creation
- Webhook handling for payment events

```https
POST /api/v1/user/deposit/
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJh...
Content-Type: application/json

{
  "amount": value
}
```

---

## 🤝 Contributing

Pull requests are welcome!

Before submitting a PR:

- Make sure all tests pass (`python manage.py test tests`)
- Format your code with `black` and check with `flake8`

---

## 📄 License

This project is licensed under the [MIT License](LICENSE).

---

## 📬 Contact

For questions or feedback:

- Email: kol230305@gmail.com  
- Telegram: [@ViverTonick](https://t.me/ViverTonick)

---
