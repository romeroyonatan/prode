import itertools

from django.db.models import (
    Case,
    F,
    Manager,
    PositiveSmallIntegerField,
    Value,
    When,
)

from prode.apuestas.constants import (
    EMPATE,
    GANA_LOCAL,
    GANA_VISITANTE,
    PUNTOS_GANADOR,
    PUNTOS_GOLES,
)


class ApuestaManager(Manager):
    def get_puntajes(self, etapa):
        """Obtiene puntajes obtenidos por los usuario en la etapa.

        Devuelve una lista de tuplas ordenadas de mayor a menor por puntajes.
        Las tuplas tienen la forma (nombre de usuario, puntos)

        :param etapa: Etapa que se quiere obtener puntajes
        :type etapa: ``models.Etapa``

        :returns: Lista de tuplas
        """
        queryset = (
            self.get_queryset()
            .filter(partido__etapa=etapa)
            .annotate(
                # Logica del puntaje
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
        )
        # obtengo puntajes sumados por usuario
        puntajes_sumados = [
            (user, sum(puntos for _, puntos in group))
            for user, group in itertools.groupby(queryset, key=lambda x: x[0])
        ]
        # ordeno por cantidad de puntos descendente
        return sorted(puntajes_sumados, key=lambda x: -x[1])
