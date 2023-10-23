from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from planetarium.models import AstronomyShow, ShowTheme
from planetarium.serializers import (
    AstronomyShowListSerializer,
    AstronomyShowDetailSerializer,
)

ASTRONOMY_SHOW_URL = reverse("planetarium:astronomyshow-list")


def sample_astronomy_show(**params) -> AstronomyShow:
    defaults = {
        "title": "Sample movie",
        "description": "Sample description",
    }
    defaults.update(params)

    return AstronomyShow.objects.create(**defaults)


class UnauthenticatedAstronomyShowApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        res = self.client.get(ASTRONOMY_SHOW_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthenticatedAstronomyShowApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            "test_user",
            "pass123",
        )
        self.client.force_authenticate(self.user)

    def test_list_astronomy_shows(self):
        sample_astronomy_show()
        sample_astronomy_show()

        res = self.client.get(ASTRONOMY_SHOW_URL)

        movies = AstronomyShow.objects.all()
        serializer = AstronomyShowListSerializer(movies, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_list_astronomy_shows_with_filters(self):
        astronomy_show1 = sample_astronomy_show(
            title="Sample astronomy show 1"
        )
        astronomy_show2 = sample_astronomy_show(
            title="Sample astronomy show 2"
        )

        res = self.client.get(ASTRONOMY_SHOW_URL, {"title": "1"})

        serializer1 = AstronomyShowListSerializer(astronomy_show1)
        serializer2 = AstronomyShowListSerializer(astronomy_show2)

        self.assertIn(serializer1.data, res.data)
        self.assertNotIn(serializer2.data, res.data)

    def test_list_astronomy_shows_with_filters_by_show_themes(self):
        astronomy_show1 = sample_astronomy_show(
            title="Sample astronomy show 1"
        )
        astronomy_show2 = sample_astronomy_show(
            title="Sample astronomy show 2"
        )
        astronomy_show1.show_themes.add(
            ShowTheme.objects.create(name="Sample theme 1")
        )
        astronomy_show2.show_themes.add(
            ShowTheme.objects.create(name="Sample theme 2")
        )

        res = self.client.get(ASTRONOMY_SHOW_URL, {"show_themes": "1"})

        serializer1 = AstronomyShowListSerializer(astronomy_show1)
        serializer2 = AstronomyShowListSerializer(astronomy_show2)

        self.assertIn(serializer1.data, res.data)
        self.assertNotIn(serializer2.data, res.data)

    def test_retrieve_astronomy_shows(self):
        astronomy_show = sample_astronomy_show()
        url = reverse(
            "planetarium:astronomyshow-detail", args=[astronomy_show.id]
        )

        res = self.client.get(url)

        serializer = AstronomyShowDetailSerializer(astronomy_show)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_create_astronomy_show_forbidden(self):
        payload = {
            "title": "Sample astronomy show",
            "description": "Sample description",
        }

        res = self.client.post(ASTRONOMY_SHOW_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)


class AdminMovieApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            "test_admin", "pass123", is_staff=True
        )
        self.client.force_authenticate(self.user)

    def test_create_astronomy_show(self):
        payload = {
            "title": "Sample astronomy show",
            "description": "Sample description",
        }

        res = self.client.post(ASTRONOMY_SHOW_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        astronomy_show = AstronomyShow.objects.get(id=res.data["id"])
        for key in payload.keys():
            self.assertEqual(payload[key], getattr(astronomy_show, key))

    def test_create_astronomy_show_with_show_themes(self):
        show_theme1 = ShowTheme.objects.create(name="Sample theme 1")
        show_theme2 = ShowTheme.objects.create(name="Sample theme 2")
        payload = {
            "title": "Sample astronomy show",
            "description": "Sample description",
            "show_themes": [show_theme1.id, show_theme2.id],
        }

        res = self.client.post(ASTRONOMY_SHOW_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        astronomy_show = AstronomyShow.objects.get(id=res.data["id"])
        show_themes = astronomy_show.show_themes.all()
        self.assertEqual(show_themes.count(), 2)
        self.assertIn(show_theme1, show_themes.all())
        self.assertIn(show_theme2, show_themes.all())
