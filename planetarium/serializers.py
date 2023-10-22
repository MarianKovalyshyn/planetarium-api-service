from rest_framework import serializers

from planetarium.models import (
    ShowTheme,
    AstronomyShow,
    ShowSession,
    PlanetariumDome,
    Ticket,
    Reservation,
)


class AstronomyShowSerializer(serializers.ModelSerializer):
    class Meta:
        model = AstronomyShow


class ShowThemeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShowTheme


class ShowSessionSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShowSession


class PlanetariumDomeSerializer(serializers.ModelSerializer):
    class Meta:
        model = PlanetariumDome


class TicketSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ticket


class ReservationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Reservation
