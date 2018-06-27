from datetime import timedelta

from django.utils import timezone

from test_plus.test import TestCase

from prode.apuestas import (
    constants,
    models,
)

from . import factories


class ApuestaManagerTests(TestCase):
    def get_etapa(self):
        """Obtiene una etapa con 5 partidos con apuestas para probar"""
        etapa = factories.EtapaFactory()
        user1 = self.make_user('user1')
        user2 = self.make_user('user2')
        user3 = self.make_user('user3')
        for _ in range(5):
            partido = factories.PartidoFactory(
                goles_local=2,
                goles_visitante=2,
                etapa=etapa,
            )
            # solo acierta goles = 3 puntos
            factories.ApuestaFactory(
                ganador=constants.GANA_LOCAL,
                goles_local=partido.goles_local,
                goles_visitante=partido.goles_visitante,
                partido=partido,
                usuario=user1,
            )
            # solo acierta empate y goles = 4 puntos
            factories.ApuestaFactory(
                ganador=constants.EMPATE,
                goles_local=partido.goles_local,
                goles_visitante=partido.goles_visitante,
                partido=partido,
                usuario=user2,
            )
            # solo acierta empate = 1 punto
            factories.ApuestaFactory(
                ganador=constants.EMPATE,
                goles_local=1,
                goles_visitante=2,
                partido=partido,
                usuario=user3,
            )
        return etapa

    def test_get_puntajes(self):
        etapa = self.get_etapa()
        expected = [
            ('user2', 20),
            ('user1', 15),
            ('user3', 5),
        ]
        puntajes = models.Apuesta.objects.get_puntajes(etapa=etapa)
        self.assertEqual(puntajes, expected)


class PartidoManagerTests(TestCase):
    def test_terminados(self):
        terminado = timezone.now() - timedelta(hours=2)
        factories.PartidoFactory(fecha=terminado)
        self.assertEqual(models.Partido.objects.terminados().count(), 1)

    def test_partido_en_juego(self):
        factories.PartidoFactory(fecha=timezone.now())
        self.assertEqual(models.Partido.objects.terminados().count(), 0)
        self.assertEqual(models.Partido.objects.no_empezados().count(), 0)


    def test_no_empezados(self):
        factories.PartidoFactory()
        self.assertEqual(models.Partido.objects.no_empezados().count(), 1)
