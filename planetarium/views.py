from rest_framework import viewsets

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
)


class AstronomyShowViewSet(viewsets.ModelViewSet):
    queryset = AstronomyShow.objects.prefetch_related("show_theme")
    serializer_class = AstronomyShowSerializer


class ShowThemeViewSet(viewsets.ModelViewSet):
    queryset = ShowTheme.objects.all()
    serializer_class = ShowThemeSerializer


class ShowSessionViewSet(viewsets.ModelViewSet):
    queryset = ShowSession.objects.select_related(
        "astronomy_show", "planetarium_dome"
    )
    serializer_class = ShowSessionSerializer


class PlanetariumDomeViewSet(viewsets.ModelViewSet):
    queryset = PlanetariumDome.objects.all()
    serializer_class = PlanetariumDomeSerializer


class TicketViewSet(viewsets.ModelViewSet):
    queryset = Ticket.objects.select_related("show_session", "reservation")
    serializer_class = TicketSerializer


class ReservationViewSet(viewsets.ModelViewSet):
    queryset = Reservation.objects.select_related("user")
    serializer_class = ReservationSerializer
