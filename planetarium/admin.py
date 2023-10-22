from django.contrib import admin


from .models import (
    AstronomyShow,
    ShowTheme,
    ShowSession,
    PlanetariumDome,
    Ticket,
    Reservation,
)

admin.register(AstronomyShow)
admin.register(ShowTheme)
admin.register(ShowSession)
admin.register(PlanetariumDome)
admin.register(Ticket)
admin.register(Reservation)
