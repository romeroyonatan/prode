from django.contrib.auth.models import AbstractUser
from django.db import models
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _


class User(AbstractUser):

    # First Name and Last Name do not cover name patterns
    # around the globe.
    name = models.CharField(_("Name of User"), blank=True, max_length=255)

    def __str__(self):
        return self.username

    def get_absolute_url(self):
        return reverse("users:detail", kwargs={"username": self.username})

    def get_puntaje(self):
        """Obtiene el puntaje de todas sus apuestas."""
        apuestas = self.apuestas.filter(
            partido__goles_local__isnull=False,
            partido__goles_visitante__isnull=False,
        )
        return sum(apuesta.puntaje for apuesta in apuestas)
