from collections import namedtuple

from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse
from django.utils import timezone
from django.views.generic import DetailView, ListView, RedirectView, UpdateView

from prode.apuestas import models as apuestas_models

from .models import User



def get_puntaje(usuario, etapa):
    """Obtiene una tupla de (etapa, apuestas, puntos).

    Los puntos es la sumatoria del puntaje obtenido por el usuario en la etapa
    """
    EtapaApostada = namedtuple('EtapaApostada', 'etapa apuestas puntos')
    apuestas = apuestas_models.Apuesta.objects.filter(
        partido__etapa=etapa,
        usuario=usuario,
    ).prefetch_related('partido')
    puntaje = usuario.apuestas.ranking(apuestas)
    if not puntaje:
        return EtapaApostada(etapa, apuestas, 0)
    return EtapaApostada(etapa, apuestas, puntaje[0].puntos)


class UserDetailView(LoginRequiredMixin, DetailView):
    model = User
    # These next two lines tell the view to index lookups by username
    slug_field = "username"
    slug_url_kwarg = "username"

    def get_context_data(self, **kwargs):
        kwargs['etapas_apostadas'] = self.get_etapas_apostadas()
        return super().get_context_data(**kwargs)

    def get_etapas_apostadas(self):
        """Obtiene tupla de tuplas (etapa, apuestas, puntos) en las que el
        usuario haya apostado

        Los puntos son la suma de puntos obtenidos en dicha etapa

        Solo muestro etapas que ya esten vencidas para evitar leak de
        informacion
        """
        usuario = self.get_object()
        etapas = apuestas_models.Etapa.objects.filter(
            vencimiento__lt=timezone.now(),
            partidos__apuestas__usuario=usuario,
        ).distinct()
        return tuple(get_puntaje(usuario, etapa) for etapa in etapas)


class UserRedirectView(LoginRequiredMixin, RedirectView):
    permanent = False

    def get_redirect_url(self):
        return '/'


class UserUpdateView(LoginRequiredMixin, UpdateView):

    fields = ["name"]

    # we already imported User in the view code above, remember?
    model = User

    # send the user back to their own page after a successful update

    def get_success_url(self):
        return reverse("users:detail", kwargs={"username": self.request.user.username})

    def get_object(self):
        # Only get the User record for the user making the request
        return User.objects.get(username=self.request.user.username)


class UserListView(LoginRequiredMixin, ListView):
    model = User
    # These next two lines tell the view to index lookups by username
    slug_field = "username"
    slug_url_kwarg = "username"
