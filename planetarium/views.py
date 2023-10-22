from typing import Type

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.serializers import ModelSerializer

from planetarium.models import (
    AstronomyShow,
    ShowTheme,
    ShowSession,
    PlanetariumDome,
    Reservation,
)
from planetarium.serializers import (
    AstronomyShowSerializer,
    ShowThemeSerializer,
    ShowSessionSerializer,
    PlanetariumDomeSerializer,
    ReservationSerializer,
    AstronomyShowListSerializer,
    ShowSessionListSerializer,
    ReservationListSerializer,
    AstronomyShowImageSerializer,
)


class AstronomyShowViewSet(viewsets.ModelViewSet):
    queryset = AstronomyShow.objects.prefetch_related("show_theme")
    serializer_class = AstronomyShowSerializer

    def get_serializer_class(self) -> Type[ModelSerializer]:
        if self.action == "list" or self.action == "retrieve":
            return AstronomyShowListSerializer
        if self.action == "upload_image":
            return AstronomyShowImageSerializer
        return AstronomyShowSerializer

    @action(
        methods=["POST"],
        detail=True,
        url_path="upload-image",
    )
    def upload_image(self, request, pk=None) -> Response:
        astronomy_show = self.get_object()
        serializer = self.get_serializer(astronomy_show, data=request.data)

        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data, status=status.HTTP_200_OK)


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
