import os
import tempfile
from datetime import timedelta
from decimal import Decimal

from PIL import Image
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
from django.utils.timezone import now
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APITestCase

from airport.models import AirplaneType, Airplane, Crew, Flight, Airport, Route, Order, Ticket
from tests.test_user import sample_user

MEDIA_ROOT = tempfile.mkdtemp()


class TestPermissions(APITestCase):

    def setUp(self):
        self.user = sample_user()
        self.admin = sample_user(email="admin@admin.com", is_staff=True, is_superuser=True)
        self.airplane_type = AirplaneType.objects.create(name="Airplane")
        self.list_url = reverse("airport:airplane-type-list")
        self.detail_url = reverse("airport:airplane-type-detail", kwargs={"pk": self.airplane_type.id})
        self.payload = {
            "name": "Test"
        }

    def test_unauthorized(self):
        res = self.client.get(self.list_url)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)
        res = self.client.post(self.list_url, data=self.payload)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)
        res = self.client.get(self.detail_url)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)
        res = self.client.patch(self.detail_url, data=self.payload)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)
        res = self.client.put(self.detail_url, data=self.payload)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_authorized(self):
        self.client.force_authenticate(self.user)
        res = self.client.get(self.list_url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        res = self.client.post(self.list_url, data=self.payload)
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)
        res = self.client.get(self.detail_url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        res = self.client.patch(self.detail_url, data=self.payload)
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)
        res = self.client.put(self.detail_url, data=self.payload)
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_admin(self):
        self.client.force_authenticate(self.admin)
        res = self.client.get(self.list_url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        res = self.client.post(self.list_url, data=self.payload)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        res = self.client.get(self.detail_url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        res = self.client.patch(self.detail_url, data=self.payload)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        res = self.client.put(self.detail_url, data=self.payload)
        self.assertEqual(res.status_code, status.HTTP_200_OK)


class TestRouteDistance(TestCase):

    def setUp(self):
        self.source = Airport.objects.create(
            name="Boryspil International Airport",
            IATA_code="KBP",
            ICAO_code="UKBB",
            closest_big_city="Kyiv",
            timezone="Europe/Kyiv",
            latitude=Decimal("50.345000"),
            longitude=Decimal("30.894722"),
        )

        self.destination = Airport.objects.create(
            name="Frankfurt am Main Airport",
            IATA_code="FRA",
            ICAO_code="EDDF",
            closest_big_city="Frankfurt",
            timezone="Europe/Berlin",
            latitude=Decimal("50.033333"),
            longitude=Decimal("8.570556"),
        )

    def test_route_distance_calculation(self):
        route = Route.objects.create(
            source=self.source,
            destination=self.destination
        )

        expected_distance = route.haversine_distance(
            self.source.latitude,
            self.source.longitude,
            self.destination.latitude,
            self.destination.longitude
        )

        self.assertEqual(
            route.distance,
            expected_distance,
            f"Expected distance {expected_distance}, got {route.distance}"
        )


class TestFlightCreation(APITestCase):

    def setUp(self):
        self.user = sample_user(is_staff=True, is_superuser=True)
        self.client.force_authenticate(self.user)
        self.airport1 = Airport.objects.create(
            name="Boryspil International Airport",
            IATA_code="KBP",
            ICAO_code="UKBB",
            closest_big_city="Kyiv",
            timezone="Europe/Kyiv",
            latitude=Decimal("50.345000"),
            longitude=Decimal("30.894722"),
        )
        self.airport2 = Airport.objects.create(
            name="Frankfurt am Main Airport",
            IATA_code="FRA",
            ICAO_code="EDDF",
            closest_big_city="Frankfurt",
            timezone="Europe/Berlin",
            latitude=Decimal("50.033333"),
            longitude=Decimal("8.570556"),
        )
        self.route = Route.objects.create(source=self.airport1, destination=self.airport2)
        self.airplane_type = AirplaneType.objects.create(name="Boeing 737")
        self.airplane = Airplane.objects.create(
            type=self.airplane_type,
            tail_number="UR-XYZ",
            manufacturer="BOEING",
            model="737-800",
            rows=30,
            seats_in_row=6,
        )
        now_time = now()
        self.departure_time = now_time + timedelta(days=1)
        self.arrival_time = now_time + timedelta(days=1, hours=2)
        self.crew_pilot = Crew.objects.create(
            first_name="Ivan",
            last_name="Ivanov",
            role="PILOT",
            license_number="LIC001",
            license_expiration=now_time + timedelta(days=30),
        )
        self.crew_copilot = Crew.objects.create(
            first_name="Petr",
            last_name="Petrov",
            role="CO-PILOT",
            license_number="LIC002",
            license_expiration=now_time + timedelta(days=30),
        )
        self.crew_attendant = Crew.objects.create(
            first_name="Anna",
            last_name="Andreeva",
            role="FLIGHT_ATTENDANT",
            license_number="LIC003",
            license_expiration=now_time + timedelta(days=30),
        )
        self.crew_engineer = Crew.objects.create(
            first_name="Oleg",
            last_name="Ivanov",
            role="ENGINEER",
            license_number="LIC004",
            license_expiration=now_time + timedelta(days=30),
        )
        self.flight_url = reverse("airport:flight-list")
        self.data = {
            "airplane": self.airplane.id,
            "route": self.route.id,
            "departure_time": self.departure_time.isoformat(),
            "arrival_time": self.arrival_time.isoformat(),
        }

    def test_create_flight_successful(self):
        self.data["crew"] = [self.crew_pilot.pk, self.crew_copilot.pk, self.crew_attendant.pk]

        response = self.client.post(self.flight_url, self.data, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Flight.objects.count(), 1)
        flight = Flight.objects.first()
        self.assertEqual(flight.crew.count(), 3)

    def test_create_flight_crew_less_than_3(self):
        self.data["crew"] = [self.crew_copilot.pk, self.crew_attendant.pk]
        response = self.client.post(self.flight_url, self.data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Flight.objects.count(), 0)
        self.assertIn("There should be at least 3 crew on a flight", response.content.decode())

    def test_create_flight_with_expired_crew(self):
        self.crew_pilot.license_expiration = now() - timedelta(days=1)
        self.crew_pilot.save()
        self.data["crew"] = [self.crew_pilot.pk, self.crew_copilot.pk, self.crew_attendant.pk]
        response = self.client.post(self.flight_url, self.data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Flight.objects.count(), 0)
        self.assertIn(f"{self.crew_pilot.full_name} has an expired license.", response.content.decode())

    def test_create_flight_without_required_role(self):
        crews = [
            ([self.crew_engineer.pk, self.crew_copilot.pk, self.crew_attendant.pk], "Flight must include a PILOT."),
            ([self.crew_pilot.pk, self.crew_engineer.pk, self.crew_attendant.pk], "Flight must include a CO-PILOT."),
            ([self.crew_pilot.pk, self.crew_copilot.pk, self.crew_engineer.pk], "Flight must include at least one FLIGHT_ATTENDANT.")
        ]
        for crew_set, message in crews:
            self.data["crew"] = crew_set

            response = self.client.post(self.flight_url, self.data, format="json")

            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
            self.assertEqual(Flight.objects.count(), 0)
            self.assertIn(message, response.content.decode())


class TestUserOrder(APITestCase):

    def setUp(self):
        self.user = sample_user(balance=500)
        self.client.force_authenticate(self.user)
        airplane_type = AirplaneType.objects.create(name="Airplane")
        self.airplane = Airplane.objects.create(
            type=airplane_type,
            tail_number="123",
            manufacturer="AIRBUS",
            rows=10,
            seats_in_row=10,
        )
        pilot = Crew.objects.create(
            first_name="Pilot",
            last_name="Pilot",
            role="PILOT",
            license_number="123",
            license_expiration=now() + timedelta(days=1),
        )
        copilot = Crew.objects.create(
            first_name="Co-Pilot",
            last_name="Co-Pilot",
            role="CO-PILOT",
            license_number="1234",
            license_expiration=now() + timedelta(days=1),
        )
        attendant = Crew.objects.create(
            first_name="Attendant",
            last_name="Attendant",
            role="FLIGHT_ATTENDANT",
            license_number="12345",
            license_expiration=now() + timedelta(days=1),
        )
        airport1 = Airport.objects.create(
            name="Boryspil International Airport",
            IATA_code="KBP",
            ICAO_code="UKBB",
            closest_big_city="Kyiv",
            timezone="Europe/Kiev",
            latitude=50.345001,
            longitude=30.894699
        )
        airport2 = Airport.objects.create(
            name="Frankfurt am Main Airport",
            IATA_code="FRA",
            ICAO_code="EDDF",
            closest_big_city="Frankfurt",
            timezone="Europe/Berlin",
            latitude=50.037933,
            longitude=8.562152
        )
        route = Route.objects.create(
            source=airport1,
            destination=airport2,
        )
        self.flight = Flight.objects.create(
            airplane=self.airplane,
            route=route,
            departure_time=now() + timedelta(days=1),
            arrival_time=now() + timedelta(days=2),
        )
        self.flight.crew.add(copilot, attendant, pilot)
        self.url = reverse("airport:order-list")

    def test_order_successful(self):
        payload = {
            "tickets": [
                {
                    "row": 1,
                    "seat": 1,
                    "flight": str(self.flight.pk)
                }
            ]
        }
        res = self.client.post(self.url, payload, content_type="application/json")
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Flight.objects.count(), 1)
        order = Order.objects.first()
        self.assertEqual(order.status, "PAID")

    def test_with_no_balance(self):
        self.user.balance = 0
        self.user.save()
        payload = {
            "tickets": [
                {
                    "row": 1,
                    "seat": 1,
                    "flight": str(self.flight.pk)
                }
            ]
        }
        res = self.client.post(self.url, payload, content_type="application/json")
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("Not enough on balance", res.content.decode())

    def test_order_ongoing_flight(self):
        self.flight.departure_time = now()
        self.flight.arrival_time = now() + timedelta(days=1)
        self.flight.save()
        payload = {
            "tickets": [
                {
                    "row": 1,
                    "seat": 1,
                    "flight": str(self.flight.pk)
                }
            ]
        }
        res = self.client.post(self.url, payload, content_type="application/json")
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("Flight is completed or ongoing.", res.content.decode())

    def test_order_not_existing_seat(self):
        payload = {
            "tickets": [
                {
                    "row": self.airplane.rows + 1,
                    "seat": self.airplane.seats_in_row + 1,
                    "flight": str(self.flight.pk)
                }
            ]
        }
        res = self.client.post(self.url, payload, content_type="application/json")
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("No such seat on this plane.", res.content.decode())

    def test_order_existing_ticket(self):
        order = Order.objects.create(
            user=self.user,
        )
        ticket = Ticket.objects.create(
            flight=self.flight,
            row=1,
            seat=1,
            order=order,
            price=self.flight.price,
        )
        payload = {
            "tickets": [
                {
                    "row": ticket.row,
                    "seat": ticket.seat,
                    "flight": str(self.flight.pk)
                }
            ]
        }
        res = self.client.post(self.url, payload, content_type="application/json")
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("The fields row, seat, flight must make a unique set.", res.content.decode())

    def test_order_duplicate_ticket(self):
        payload = {
            "tickets": [
                {
                    "row": 1,
                    "seat": 1,
                    "flight": str(self.flight.pk)
                },
                {
                    "row": 1,
                    "seat": 1,
                    "flight": str(self.flight.pk)
                }
            ]
        }
        res = self.client.post(self.url, payload, content_type="application/json")
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("Duplicate seat 1-1", res.content.decode())


@override_settings(MEDIA_ROOT=MEDIA_ROOT)
class AirplaneImageTest(APITestCase):

    def setUp(self):
        self.user = sample_user(is_staff=True, is_superuser=True)
        self.client.force_authenticate(self.user)
        self.airplane_type = AirplaneType.objects.create(name="Boeing 737")
        airplane_type = AirplaneType.objects.create(name="Airplane")
        self.airplane = Airplane.objects.create(
            type=airplane_type,
            tail_number="123",
            manufacturer="AIRBUS",
            model="123",
            rows=10,
            seats_in_row=10,
        )
        self.url = reverse("airport:airplane-set-image", kwargs={"pk": self.airplane.pk})

    def generate_test_image(self):
        image = Image.new("RGB", (100, 100), color="red")
        temp_file = tempfile.NamedTemporaryFile(suffix=".jpg", delete=False)
        image.save(temp_file, format="JPEG")
        temp_file.seek(0)
        return temp_file

    def test_set_image_and_delete(self):
        temp_image = self.generate_test_image()
        with open(temp_image.name, "rb") as img:
            uploaded = SimpleUploadedFile("test.jpg", img.read(), content_type="image/jpeg")

        response = self.client.post(self.url, {"image": uploaded}, format="multipart")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.airplane.refresh_from_db()
        image_path = self.airplane.image.path
        self.assertTrue(os.path.isfile(image_path))

        url = reverse("airport:airplane-delete-image", kwargs={"pk": self.airplane.pk})
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.airplane.refresh_from_db()
        self.assertFalse(os.path.isfile(image_path))

    def test_image_changed(self):
        temp_image = self.generate_test_image()
        with open(temp_image.name, "rb") as img:
            uploaded = SimpleUploadedFile("test1.jpg", img.read(), content_type="image/jpeg")

        self.client.post(self.url, {"image": uploaded}, format="multipart")

        self.airplane.refresh_from_db()
        image_path1 = self.airplane.image.path

        with open(temp_image.name, "rb") as img:
            uploaded = SimpleUploadedFile("test2.jpg", img.read(), content_type="image/jpeg")
        self.client.post(self.url, {"image": uploaded}, format="multipart")
        self.airplane.refresh_from_db()
        image_path2 = self.airplane.image.path

        self.assertFalse(os.path.isfile(image_path1))
        self.assertTrue(os.path.isfile(image_path2))
        self.airplane.image.delete()

    def test_image_airplane_deleted(self):
        temp_image = self.generate_test_image()
        with open(temp_image.name, "rb") as img:
            uploaded = SimpleUploadedFile("test1.jpg", img.read(), content_type="image/jpeg")

        self.client.post(self.url, {"image": uploaded}, format="multipart")

        self.airplane.refresh_from_db()
        image_path = self.airplane.image.path
        url = reverse("airport:airplane-detail", kwargs={"pk": self.airplane.pk})
        res = self.client.delete(url)
        print(res.content.decode())
        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(os.path.isfile(image_path))
