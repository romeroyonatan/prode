import datetime

from django.utils import timezone
from test_plus import TestCase

from prode.apuestas import constants
from . import factories


class EtapaTests(TestCase):
    def test_str(self):
        etapa = factories.EtapaFactory.build(nombre='Octavos de final')
        self.assertEqual(str(etapa), 'Octavos de final')

    def test_get_absolute_url__etapa_vencida(self):
        etapa = factories.EtapaFactory.build(slug='foo',
                                             vencimiento=timezone.now())
        expected = '/foo/'
        self.assertEqual(etapa.get_absolute_url(), expected)

    def test_get_absolute_url__etapa_no_vencida(self):
        fecha_futura = timezone.now() + datetime.timedelta(days=1)
        etapa = factories.EtapaFactory.build(slug='foo',
                                             vencimiento=fecha_futura)
        expected = '/foo/apostar/'
        self.assertEqual(etapa.get_absolute_url(), expected)

    def test_get_absolute_url__no_publica(self):
        etapa = factories.EtapaFactory.build(slug='foo', publica=False)
        expected = '/foo/editar/'
        self.assertEqual(etapa.get_absolute_url(), expected)

    def test_vencida(self):
        etapa = factories.EtapaFactory.build(slug='foo',
                                             vencimiento=timezone.now())
        self.assertTrue(etapa.vencida)

    def test_no_vencida(self):
        fecha_futura = timezone.now() + datetime.timedelta(days=1)
        etapa = factories.EtapaFactory.build(slug='foo',
                                             vencimiento=fecha_futura)
        self.assertFalse(etapa.vencida)


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
            self.assertFalse(partido.resultado)

    def test_str(self):
        partido = factories.PartidoFactory.build(local='AR',
                                                 visitante='BR',
                                                 goles_local=None,
                                                 goles_visitante=None)
        self.assertEqual(str(partido), 'Argentina - Brazil')

    def test_str_partido_terminado(self):
        partido = factories.PartidoFactory.build(local='AR',
                                                 visitante='BR',
                                                 goles_local=1,
                                                 goles_visitante=2)
        self.assertEqual(str(partido), 'Argentina 1 - 2 Brazil')


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
                                           partido__goles_local=None,
                                           partido__visitante='BR',
                                           partido__goles_visitante=None,
                                           usuario__username='fulano')
        self.assertEqual(str(apuesta),
                         'Apuesta "Argentina - Brazil" por fulano')
