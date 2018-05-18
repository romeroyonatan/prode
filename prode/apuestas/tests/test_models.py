from test_plus import TestCase

from prode.apuestas import (
    constants,
    models,
)
from . import factories


class Etapa(TestCase):
    def test_str(self):
        etapa = factories.EtapaFactory.build(nombre='Octavos de final')
        self.assertEqual(str(etapa), 'Octavos de final')


class PartidoTests(TestCase):
    def test_resultado_empate(self):
        partido = factories.PartidoFactory(goles_local=1, goles_visitante=1)
        self.assertEqual(partido.resultado, constants.EMPATE)

    def test_resultado_gana_local(self):
        partido = factories.PartidoFactory(goles_local=1, goles_visitante=0)
        self.assertEqual(partido.resultado, constants.GANA_LOCAL)

    def test_resultado_gana_visitante(self):
        partido = factories.PartidoFactory(goles_local=1, goles_visitante=3)
        self.assertEqual(partido.resultado, constants.GANA_VISITANTE)

    def test_partido_indefindo(self):
        partido = factories.PartidoFactory(goles_local=None,
                                           goles_visitante=None)
        with self.assertRaises(ValueError):
            partido.resultado

    def test_str(self):
        partido = factories.PartidoFactory.build(local='AR', visitante='BR')
        self.assertEqual(str(partido), 'Argentina - Brazil')


class ApuestaTests(TestCase):
    def test_puntaje_sin_coincidencia(self):
        partido = factories.PartidoFactory(goles_local=1, goles_visitante=0)
        apuesta = factories.ApuestaFactory(partido=partido,
                                           goles_local=1,
                                           goles_visitante=1,
                                           ganador=constants.EMPATE)
        self.assertEqual(apuesta.puntaje, 0)

    def test_puntaje_acierta_empate(self):
        partido = factories.PartidoFactory(goles_local=0, goles_visitante=0)
        apuesta = factories.ApuestaFactory(partido=partido,
                                           goles_local=1,
                                           goles_visitante=1,
                                           ganador=constants.EMPATE)
        self.assertEqual(apuesta.puntaje, 1)

    def test_puntaje_acierta_ganador_local(self):
        partido = factories.PartidoFactory(goles_local=1, goles_visitante=0)
        apuesta = factories.ApuestaFactory(partido=partido,
                                           goles_local=1,
                                           goles_visitante=1,
                                           ganador=constants.GANA_LOCAL)
        self.assertEqual(apuesta.puntaje, 1)

    def test_puntaje_acierta_ganador_visitante(self):
        partido = factories.PartidoFactory(goles_local=0, goles_visitante=1)
        apuesta = factories.ApuestaFactory(partido=partido,
                                           goles_local=0,
                                           goles_visitante=2,
                                           ganador=constants.GANA_VISITANTE)
        self.assertEqual(apuesta.puntaje, 1)

    def test_puntaje_acierta_goles(self):
        partido = factories.PartidoFactory(goles_local=0, goles_visitante=1)
        apuesta = factories.ApuestaFactory(partido=partido,
                                           goles_local=0,
                                           goles_visitante=1,
                                           ganador=constants.EMPATE)
        self.assertEqual(apuesta.puntaje, 3)

    def test_puntaje_acierta_ganador_y_goles(self):
        partido = factories.PartidoFactory(goles_local=0, goles_visitante=1)
        apuesta = factories.ApuestaFactory(partido=partido,
                                           goles_local=0,
                                           goles_visitante=1,
                                           ganador=constants.GANA_VISITANTE)
        self.assertEqual(apuesta.puntaje, 4)

    def test_str(self):
        apuesta = factories.ApuestaFactory(partido__local='AR',
                                           partido__visitante='BR',
                                           usuario__username='fulano')
        self.assertEqual(str(apuesta),
                         'Apuesta "Argentina - Brazil" por fulano')
