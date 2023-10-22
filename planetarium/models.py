from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models


class AstronomyShow(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    ShowTheme = models.ManyToManyField("ShowTheme")

    class Meta:
        ordering = ["title"]

    def __str__(self) -> str:
        return self.title


class ShowTheme(models.Model):
    name = models.CharField(max_length=255, unique=True)

    def __str__(self) -> str:
        return self.name


class ShowSession(models.Model):
    astronomy_show = models.ForeignKey("AstronomyShow", on_delete=models.CASCADE)
    planetarium_dome = models.ForeignKey("PlanetariumDome", on_delete=models.CASCADE)
    show_time = models.DateTimeField()

    def __str__(self) -> str:
        return f"{self.astronomy_show} - {self.show_time} at {self.planetarium_dome}"


class PlanetariumDome(models.Model):
    name = models.CharField(max_length=255)
    rows = models.IntegerField()
    seats_in_row = models.IntegerField()

    @property
    def capacity(self) -> int:
        return self.rows * self.seats_in_row

    def __str__(self) -> str:
        return f"{self.name} - {self.capacity} seats"


class Ticket(models.Model):
    row = models.IntegerField()
    seat = models.IntegerField()
    show_session = models.ForeignKey("ShowSession", on_delete=models.CASCADE)
    reservation = models.ForeignKey("Reservation", on_delete=models.CASCADE)

    def __str__(self) -> str:
        return f"{self.show_session} (row: {self.row}, seat: {self.seat}) by {self.reservation}"


class Reservation(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    def __str__(self) -> str:
        return f"{str(self.created_at)} by {self.user}"


class User(AbstractUser):
    pass
