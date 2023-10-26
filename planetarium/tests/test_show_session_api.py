from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from planetarium.models import (
    ShowSession,
    AstronomyShow,
    PlanetariumDome,
)
from planetarium.serializers import (
    ShowSessionListSerializer,
    ShowSessionDetailSerializer,
)

SHOW_SESSION_URL = reverse("planetarium:showsession-list")


def sample_show_session(**params) -> ShowSession:
    defaults = {
        "title": "Sample astronomy show",
        "description": "Sample description",
        "name": "Sample planetarium dome",
        "rows": 5,
        "seats_in_row": 10,
        "show_time": "2023-01-01T12:00:00Z",
    }
    defaults.update(params)

    astronomy_show = AstronomyShow.objects.create(
        title=defaults.pop("title"),
        description=defaults.pop("description"),
    )
    planetarium_dome = PlanetariumDome.objects.create(
        name=defaults.pop("name"),
        rows=defaults.pop("rows"),
        seats_in_row=defaults.pop("seats_in_row"),
    )
    show_time = defaults.pop("show_time")

    return ShowSession.objects.create(
        astronomy_show=astronomy_show,
        planetarium_dome=planetarium_dome,
        show_time=show_time,
    )


class UnauthenticatedShowSessionApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        res = self.client.get(SHOW_SESSION_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthenticatedShowSessionApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            "test_user",
            "pass123",
        )
        self.client.force_authenticate(self.user)

    def test_list_show_sessions(self):
        sample_show_session(
            title="Sample astronomy show 2",
            description="Sample description 2",
            name="Sample planetarium dome 2",
            rows=1,
            seats_in_row=20,
            show_time="2023-02-02T12:00:00Z",
        )
        sample_show_session(
            title="Sample astronomy show 1",
            description="Sample description 1",
            name="Sample planetarium dome 1",
            rows=1,
            seats_in_row=10,
            show_time="2023-01-01T12:00:00Z",
        )

        res = self.client.get(SHOW_SESSION_URL)

        show_sessions = ShowSession.objects.all()
        serializer = ShowSessionListSerializer(show_sessions, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)

        for i in range(2):
            self.assertIn(
                serializer.data[i]["astronomy_show"],
                res.data[i]["astronomy_show"],
            )
            self.assertIn(
                serializer.data[i]["planetarium_dome"],
                res.data[i]["planetarium_dome"],
            )
            self.assertIn(
                serializer.data[i]["show_time"], res.data[i]["show_time"]
            )

    def test_list_show_sessions_with_filters_by_date(self):
        show_session1 = sample_show_session(
            title="Sample astronomy show 1",
            description="Sample description 1",
            name="Sample planetarium dome 1",
            rows=1,
            seats_in_row=10,
            show_time="2023-01-01T12:00:00Z",
        )
        show_session2 = sample_show_session(
            title="Sample astronomy show 2",
            description="Sample description 2",
            name="Sample planetarium dome 2",
            rows=1,
            seats_in_row=20,
            show_time="2023-02-02T12:00:00Z",
        )

        res = self.client.get(SHOW_SESSION_URL, {"date": "2023-01-01"})

        serializer1 = ShowSessionListSerializer(show_session1)
        serializer2 = ShowSessionListSerializer(show_session2)

        self.assertEqual(
            serializer1.data["show_time"], res.data[0]["show_time"]
        )
        self.assertNotEqual(
            serializer2.data["show_time"], res.data[0]["show_time"]
        )

    def test_list_show_sessions_with_filters_by_astronomy_show(self):
        show_session1 = sample_show_session(
            title="Sample astronomy show 1",
            description="Sample description 1",
            name="Sample planetarium dome 1",
            rows=1,
            seats_in_row=10,
            show_time="2023-01-01T12:00:00Z",
        )
        show_session2 = sample_show_session(
            title="Sample astronomy show 2",
            description="Sample description 2",
            name="Sample planetarium dome 2",
            rows=1,
            seats_in_row=20,
            show_time="2023-02-02T12:00:00Z",
        )

        res = self.client.get(SHOW_SESSION_URL, {"astronomy_show": "1"})

        serializer1 = ShowSessionListSerializer(show_session1)
        serializer2 = ShowSessionListSerializer(show_session2)

        self.assertEqual(
            serializer1.data["astronomy_show"], res.data[0]["astronomy_show"]
        )
        self.assertNotEqual(
            serializer2.data["astronomy_show"], res.data[0]["astronomy_show"]
        )

    def test_retrieve_show_session(self):
        show_session = sample_show_session()
        url = reverse("planetarium:showsession-detail", args=[show_session.id])

        res = self.client.get(url)

        serializer = ShowSessionDetailSerializer(show_session)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_create_show_session_forbidden(self):
        payload = {
            "astronomy_show": 1,
            "planetarium_dome": 1,
            "show_time": "2023-01-01T12:00:00Z",
        }

        res = self.client.post(SHOW_SESSION_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)


class AdminShowSessionApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            "test_admin", "pass123", is_staff=True
        )
        self.client.force_authenticate(self.user)

    def test_create_show_session(self):
        astronomy_show = AstronomyShow.objects.create(
            title="Sample astronomy show",
            description="Sample description",
        )
        planetarium_dome = PlanetariumDome.objects.create(
            name="Sample planetarium dome",
            rows=1,
            seats_in_row=10,
        )

        payload = {
            "astronomy_show": astronomy_show.id,
            "planetarium_dome": planetarium_dome.id,
            "show_time": "2023-01-01T12:00:00Z",
        }

        res = self.client.post(SHOW_SESSION_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
