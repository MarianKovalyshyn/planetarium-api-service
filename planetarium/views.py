from typing import Type

from rest_framework import viewsets
from rest_framework.serializers import ModelSerializer

from planetarium.models import (
    AstronomyShow,
    ShowTheme,
    ShowSession,
    PlanetariumDome,
    Ticket,
    Reservation,
)
from planetarium.serializers import (
    AstronomyShowSerializer,
    ShowThemeSerializer,
    ShowSessionSerializer,
    PlanetariumDomeSerializer,
    ReservationSerializer,
    TicketSerializer,
    AstronomyShowListSerializer,
    ShowSessionListSerializer,
    ReservationListSerializer,
)


class AstronomyShowViewSet(viewsets.ModelViewSet):
    queryset = AstronomyShow.objects.prefetch_related("show_theme")
    serializer_class = AstronomyShowSerializer

    def get_serializer_class(self) -> Type[ModelSerializer]:
        if self.action == "list" or self.action == "retrieve":
            return AstronomyShowListSerializer
        return AstronomyShowSerializer


class ShowThemeViewSet(viewsets.ModelViewSet):
    queryset = ShowTheme.objects.all()
    serializer_class = ShowThemeSerializer


class ShowSessionViewSet(viewsets.ModelViewSet):
    queryset = ShowSession.objects.select_related(
        "astronomy_show", "planetarium_dome"
    )
    serializer_class = ShowSessionSerializer

    def get_serializer_class(self) -> Type[ModelSerializer]:
        if self.action == "list" or self.action == "retrieve":
            return ShowSessionListSerializer
        return ShowSessionSerializer


class PlanetariumDomeViewSet(viewsets.ModelViewSet):
    queryset = PlanetariumDome.objects.all()
    serializer_class = PlanetariumDomeSerializer


class ReservationViewSet(viewsets.ModelViewSet):
    queryset = Reservation.objects.select_related("user").prefetch_related(
        "tickets__show_session", "tickets__reservation"
    )
    serializer_class = ReservationSerializer

    def get_serializer_class(self) -> Type[ModelSerializer]:
        if self.action == "list" or self.action == "retrieve":
            return ReservationListSerializer
        return ReservationSerializer
