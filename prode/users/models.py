from django.contrib.auth.models import AbstractUser
from django.db import models
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _

from prode.apuestas import utils


class User(AbstractUser):

    # First Name and Last Name do not cover name patterns
    # around the globe.
    name = models.CharField(_("Nombre completo"), blank=True, max_length=255)

    def __str__(self):
        return self.username

    def get_absolute_url(self):
        return reverse("users:detail", kwargs={"username": self.username})

    @property
    def puntaje(self):
        """Obtiene el puntaje de todas sus apuestas."""
        puntos = next(
            (puntaje.puntos for puntaje in self.apuestas.ranking()),
            0  # default value
        )
        return puntos

    @property
    def ranking(self):
        """Obtiene el puesto en el ranking del usuario"""
        return utils.get_ranking(self)
