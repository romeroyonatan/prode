import itertools
from collections import namedtuple
from datetime import timedelta

from django.db.models import (
    Case,
    F,
    Manager,
    PositiveSmallIntegerField,
    Value,
    When,
)
from django.utils import timezone

from prode.apuestas.constants import (
    EMPATE,
    GANA_LOCAL,
    GANA_VISITANTE,
    PUNTOS_GANADOR,
    PUNTOS_GOLES,
)


Rank = namedtuple('Rank', 'username puntos')


def por_usuario(item):
    """Funcion auxiliar para ordenar por usuario."""
    return item[0]


def por_puntaje(item):
    """Funcion auxiliar para ordenar por puntaje descendente."""
    return -item[1]


class PartidoManager(Manager):
    def terminados(self):
        """Obtiene partidos terminados"""
        terminado = timezone.now() - timedelta(minutes=105)
        return self.get_queryset().filter(fecha__lt=terminado)

    def no_empezados(self):
        """Obtiene partidos no empezados"""
        return self.get_queryset().filter(fecha__gt=timezone.now())


class ApuestaManager(Manager):
    def get_puntajes(self, etapa):
        """Obtiene puntajes obtenidos por los usuario en la etapa.

        Devuelve una lista de tuplas ordenadas de mayor a menor por puntajes.
        Las tuplas tienen la forma (nombre de usuario, puntos)

        :param etapa: Etapa que se quiere obtener puntajes
        :type etapa: ``models.Etapa``

        :returns: Lista de tuplas
        """
        queryset = self.get_queryset().filter(partido__etapa=etapa)
        return self.ranking(queryset)

    def ranking(self, queryset=None):
        """Obtiene puntajes obtenidos por los usuario en todas las etapas.

        Devuelve una lista de tuplas ordenadas de mayor a menor por puntajes.
        Las tuplas tienen la forma (nombre de usuario, puntos)

        :returns: Lista de tuplas (nombre de usuario, puntos)
        """
        if queryset is None:
            queryset = self.get_queryset()
        puntajes = (
            queryset.annotate(
                # Puntos por ganador
                puntos_ganador=Case(
                    When(ganador=GANA_LOCAL,
                         partido__goles_local__gt=F('partido__goles_visitante'),
                         then=Value(PUNTOS_GANADOR)),
                    When(ganador=GANA_VISITANTE,
                         partido__goles_visitante__gt=F('partido__goles_local'),
                         then=Value(PUNTOS_GANADOR)),
                    When(ganador=EMPATE,
                         partido__goles_visitante=F('partido__goles_local'),
                         then=Value(PUNTOS_GANADOR)),
                    default=0,
                    output_field=PositiveSmallIntegerField(),
                ),
                # Puntos por goles
                puntos_goles=Case(
                    When(goles_local=F('partido__goles_local'),
                         goles_visitante=F('partido__goles_visitante'),
                         then=Value(PUNTOS_GOLES)),
                    default=0,
                    output_field=PositiveSmallIntegerField(),
                ),
            )
            .annotate(puntos=F('puntos_goles') + F('puntos_ganador'))
            .values_list('usuario__username', 'puntos')
            .order_by('usuario__username')
        )
        # obtengo puntajes sumados por usuario
        puntajes_sumados = [
            Rank(user, sum(puntos for _, puntos in group))
            for user, group in itertools.groupby(puntajes, key=por_usuario)
        ]
        # ordeno por cantidad de puntos de mayor a menor
        return sorted(puntajes_sumados, key=por_puntaje)
