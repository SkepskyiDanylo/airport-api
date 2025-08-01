# ✈️ Airport API

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

## ⚙️ Installation

```bash
git clone https://github.com/your-username/airport-api.git
cd airport-api
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

Create a `.env` file with the required environment variables:

```env
DEBUG=True
SECRET_KEY=secret key

# Stripe payments
STRIPE_API_KEY=api key
STRIPE_WEBHOOK_SECRET=webhook secret
SUCCESS_URL=your_url.com/success
CANCEL_URL=your_url.com/fail

# Gmail SMTP
USE_EMAIL_VERIFICATION=True
SMTP_PASSWORD=your password
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_HOST_USER=your@email.com
SMTP_DEFAULT_FROM_EMAIL=your@email.com
FRONTEND_URL=your_url.com

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
└── README.md
```

---

## ▶️ Running the Project

```bash
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

---

## 🧪 Running Tests

```bash
python manage.py test tests
```

---

## 📄 API Documentation

- Swagger: [`/swagger/`](http://localhost:8000/swagger/)
- ReDoc: [`/redoc/`](http://localhost:8000/redoc/)

---

## 🔐 Authentication & Access

- JWT-based authentication via `djangorestframework-simplejwt`
- Permissions managed using `IsAuthenticated`, `IsAdmin`, `IsAdminOrAuthenticatedReadOnly` etc.
- Email-based account activation and password reset

---

## 💳 Stripe Integration

- Stripe Checkout session creation
- Webhook handling for payment events

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
