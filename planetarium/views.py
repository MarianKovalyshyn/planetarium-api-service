from typing import Type

from django.db.models import QuerySet, F, Count
from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework import viewsets, status, generics
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
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
    ShowSessionDetailSerializer,
    AstronomyShowDetailSerializer,
    UserSerializer,
)


class ShowThemeViewSet(viewsets.ModelViewSet):
    queryset = ShowTheme.objects.all()
    serializer_class = ShowThemeSerializer


class PlanetariumDomeViewSet(viewsets.ModelViewSet):
    queryset = PlanetariumDome.objects.all()
    serializer_class = PlanetariumDomeSerializer


class AstronomyShowViewSet(viewsets.ModelViewSet):
    queryset = AstronomyShow.objects.prefetch_related("show_themes")
    serializer_class = AstronomyShowSerializer

    @staticmethod
    def _params_to_ints(qs) -> list[int]:
        """Converts a list of string IDs to a list of integers"""
        return [int(str_id) for str_id in qs.split(",")]

    def get_queryset(self) -> QuerySet[AstronomyShow]:
        """Retrieve the astronomy shows with filters"""
        title = self.request.query_params.get("title")
        show_themes = self.request.query_params.get("show_themes")

        queryset = self.queryset

        if title:
            queryset = queryset.filter(title__icontains=title)

        if show_themes:
            show_themes_ids = self._params_to_ints(show_themes)
            queryset = queryset.filter(show_themes__id__in=show_themes_ids)

        return queryset.distinct()

    def get_serializer_class(self) -> Type[ModelSerializer]:
        if self.action == "list":
            return AstronomyShowListSerializer
        if self.action == "retrieve":
            return AstronomyShowDetailSerializer
        if self.action == "upload_image":
            return AstronomyShowImageSerializer
        return AstronomyShowSerializer

    @action(
        methods=["POST"],
        detail=True,
        url_path="upload-image",
    )
    def upload_image(self, request, pk=None) -> Response:
        """Endpoint for uploading image to specific astronomy show"""
        astronomy_show = self.get_object()
        serializer = self.get_serializer(astronomy_show, data=request.data)

        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(
        parameters=[
            OpenApiParameter(
                "title",
                type=str,
                description="Filter astronomy shows by title (ex. ?title=night)",
                required=False,
            ),
            OpenApiParameter(
                "show_themes",
                type={"type": "list", "items": {"type": "number"}},
                description="Filter astronomy shows by show themes (ex. ?show_themes=2,5)",
                required=False,
            ),
        ]
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)


class ShowSessionViewSet(viewsets.ModelViewSet):
    queryset = ShowSession.objects.select_related(
        "astronomy_show", "planetarium_dome"
    ).annotate(
        tickets_available=(
            F("planetarium_dome__rows") * F("planetarium_dome__seats_in_row")
            - Count("tickets")
        )
    )
    serializer_class = ShowSessionSerializer

    def get_serializer_class(self) -> Type[ModelSerializer]:
        if self.action == "list":
            return ShowSessionListSerializer
        if self.action == "retrieve":
            return ShowSessionDetailSerializer
        return ShowSessionSerializer

    def get_queryset(self) -> QuerySet[ShowSession]:
        """Retrieve the show sessions with filters"""
        date = self.request.query_params.get("date")
        astronomy_show = self.request.query_params.get("astronomy_show")

        queryset = self.queryset

        if date:
            queryset = queryset.filter(show_time__date=date)

        if astronomy_show:
            queryset = queryset.filter(astronomy_show_id=astronomy_show)

        return queryset

    @extend_schema(
        parameters=[
            OpenApiParameter(
                "date",
                type=str,
                description="Filter show sessions by date (ex. ?date=2023-12-31)",
                required=False,
            ),
            OpenApiParameter(
                "astronomy_show",
                type=int,
                description="Filter show sessions by astronomy show (ex. ?astronomy_show=4)",
                required=False,
            ),
        ]
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)


class ReservationPagination(PageNumberPagination):
    page_size = 5
    max_page_size = 100


class ReservationViewSet(viewsets.ModelViewSet):
    queryset = Reservation.objects.prefetch_related("tickets__show_session")
    serializer_class = ReservationSerializer
    pagination_class = ReservationPagination

    def get_serializer_class(self) -> Type[ModelSerializer]:
        if self.action == "list":
            return ReservationListSerializer
        return ReservationSerializer

    def get_queryset(self) -> QuerySet[Reservation]:
        return Reservation.objects.filter(user=self.request.user)

    def perform_create(self, serializer) -> None:
        serializer.save(user=self.request.user)


class CreateUserView(generics.CreateAPIView):
    serializer_class = UserSerializer
