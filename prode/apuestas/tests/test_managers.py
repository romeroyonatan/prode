from test_plus.test import TestCase

from prode.apuestas import (
    constants,
    models,
)

from . import factories


class ApuestaManagerTests(TestCase):
    def test_get_puntajes(self):
        partido = factories.PartidoFactory(
            goles_local=2,
            goles_visitante=2,
        )
        apuesta1 = factories.ApuestaFactory(
            partido=partido,
            goles_local=partido.goles_local,
            goles_visitante=partido.goles_visitante,
            ganador=constants.GANA_LOCAL,
        )
        apuesta2 = factories.ApuestaFactory(
            partido=partido,
            goles_local=partido.goles_local,
            goles_visitante=partido.goles_visitante,
            ganador=constants.EMPATE,
        )
        apuesta3 = factories.ApuestaFactory(
            partido=partido,
            goles_local=1,
            goles_visitante=2,
            ganador=constants.EMPATE,
        )
        expected = [
            (apuesta2.usuario.username, 4),
            (apuesta1.usuario.username, 3),
            (apuesta3.usuario.username, 1),
        ]
        puntajes = models.Apuesta.objects.get_puntajes(etapa=partido.etapa)
        self.assertEqual(puntajes, expected)
