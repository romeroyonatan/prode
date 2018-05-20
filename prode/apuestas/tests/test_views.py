import datetime

from django.utils import timezone

from test_plus.test import TestCase

from prode.apuestas import (
    constants,
    forms,
    models,
)

from . import factories

class AdministrarApuestasTest(TestCase):
    def test_context(self):
        etapa = factories.EtapaFactory()
        user = self.make_user()
        with self.login(user):
            response = self.get('apuestas:apostar', slug=etapa.slug)
        self.assertIn('formset', response.context)
        self.assertIn('etapa', response.context)

    def test_get_form_kwargs(self):
        etapa = factories.EtapaFactory()
        user = self.make_user()
        with self.login(user):
            self.get('apuestas:apostar', slug=etapa.slug)
        view = self.context['view']
        kwargs = view.get_form_kwargs()
        self.assertEqual(kwargs['usuario'], user)
        self.assertEqual(kwargs['etapa'], etapa)

    def test_get_form_class(self):
        etapa = factories.EtapaFactory()
        user = self.make_user()
        with self.login(user):
            self.get('apuestas:apostar', slug=etapa.slug)
        view = self.context['view']
        form_class = view.get_form_class()
        self.assertTrue(issubclass(form_class, forms.ApuestaBaseFormSet))

    def test_form_valid(self):
        partido = factories.PartidoFactory()
        etapa = partido.etapa
        data = {
            # managenement form
            'form-TOTAL_FORMS': 1,
            'form-INITIAL_FORMS': 0,
            # end managenement form
            'form-0-ganador': constants.GANA_LOCAL,
            'form-0-goles_local': 1,
            'form-0-goles_visitante': 1,
        }
        user = self.make_user()
        with self.login(user):
            self.post('apuestas:apostar', data=data, slug=etapa.slug)
        # assertions
        self.assertTrue(models
                        .Apuesta
                        .objects
                        .filter(usuario=user,
                                partido=partido,
                                ganador=constants.GANA_LOCAL,
                                goles_local=1,
                                goles_visitante=1)
                        .exists())


class EtapaDetailView(TestCase):
    def test_etapa_en_contexto(self):
        etapa = factories.EtapaFactory()
        with self.login(self.make_user()):
            self.get('apuestas:detail', slug=etapa.slug)
        self.assertContext('etapa', etapa)

    def test_ganador(self):
        etapa = factories.EtapaFactory()
        user1 = self.make_user('user1')
        user2 = self.make_user('user2')
        for _ in range(40):
            partido = factories.PartidoFactory(etapa=etapa,
                                               goles_local=1,
                                               goles_visitante=2)
            factories.ApuestaFactory(partido=partido,
                                     usuario=user1,
                                     goles_local=1,
                                     goles_visitante=1)
            factories.ApuestaFactory(partido=partido,
                                     usuario=user2,
                                     goles_local=1,
                                     goles_visitante=2)
        with self.login(self.make_user()):
            self.get('apuestas:detail', slug=etapa.slug)
        # obtengo puntajes
        puntajes = self.context['puntajes']
        # verifico ganador
        self.assertEqual(puntajes[0][0], 'user2')


class EtapaCreateViewTests(TestCase):
    def test_context(self):
        user = self.make_user()
        with self.login(user):
            response = self.get('apuestas:create')
        self.assertIn('partidos_formset', response.context)
        self.assertIn('form', response.context)

    def test_crear_etapa(self):
        user = self.make_user()
        data = {
            # managenement form
            'partidos-TOTAL_FORMS': 1,
            'partidos-INITIAL_FORMS': 0,
            # end managenement form
            'nombre': 'foo',
            'vencimiento': '10/07/2018 00:00',
            'publica': False,

        }
        with self.login(user):
            self.post('apuestas:create', data=data)
        self.assertTrue(
            models.Etapa.objects.filter(
                nombre='foo',
                slug='foo',
                vencimiento='2018-07-10 00:00-03:00',
                publica=False
            ).exists()
        )

    def test_crear_partidos(self):
        user = self.make_user()
        data = {
            # managenement form
            'partidos-TOTAL_FORMS': 1,
            'partidos-INITIAL_FORMS': 0,
            # end managenement form
            'nombre': 'foo',
            'vencimiento': '10/07/2018 00:00',
            'publica': False,
            # partido
            'partidos-0-fecha': '11/07/2018 09:15',
            'partidos-0-local': 'AR',
            'partidos-0-visitante': 'NG',

        }
        with self.login(user):
            self.post('apuestas:create', data=data)
        self.assertTrue(
            models.Partido.objects.filter(
                etapa__nombre='foo',
                fecha='2018-07-11 09:15-03:00',
                local='AR',
                visitante='NG',
            ).exists()
        )

    def test_validar_partidos(self):
        user = self.make_user()
        data = {
            # managenement form
            'partidos-TOTAL_FORMS': 5,
            'partidos-INITIAL_FORMS': 0,
            # end managenement form
            'nombre': 'foo',
            'vencimiento': '10/07/2018 00:00',
            'publica': False,
            # partido
            'partidos-0-fecha': '11/07/2018 09:15',
            'partidos-0-local': 'AR',
            'partidos-0-visitante': 'NG',

        }
        with self.login(user):
            self.post('apuestas:create', data=data)
        self.assertEqual(models.Partido.objects.count(), 1)


class EtapaUpdateViewTests(TestCase):
    def test_context(self):
        etapa = factories.EtapaFactory()
        user = self.make_user()
        with self.login(user):
            response = self.get('apuestas:update', slug=etapa.slug)
        self.assertIn('partidos_formset', response.context)
        self.assertIn('form', response.context)

    def test_update_etapa(self):
        etapa = factories.EtapaFactory()
        user = self.make_user()
        data = {
            'nombre': 'foo',
            'vencimiento': '10/07/2018 00:00',
            'publica': False,
            # managenement form
            'partidos-TOTAL_FORMS': 1,
            'partidos-INITIAL_FORMS': 0,
            # end managenement form

        }
        with self.login(user):
            self.post('apuestas:update', data=data, slug=etapa.slug)
            self.response_302()
        self.assertTrue(
            models.Etapa.objects.filter(
                nombre='foo',
                vencimiento='2018-07-10 00:00-03:00',
                publica=False
            ).exists()
        )

    def test_crear_partidos(self):
        etapa = factories.EtapaFactory()
        user = self.make_user()
        data = {
            'nombre': 'foo',
            'vencimiento': '10/07/2018 00:00',
            'publica': False,
            # managenement form
            'partidos-TOTAL_FORMS': 1,
            'partidos-INITIAL_FORMS': 0,
            # end managenement form
            'partidos-0-etapa': etapa.id,
            'partidos-0-fecha': '11/07/2018 09:15',
            'partidos-0-local': 'AR',
            'partidos-0-visitante': 'NG',

        }
        with self.login(user):
            self.post('apuestas:update', data=data, slug=etapa.slug)
            self.response_302()
        self.assertTrue(
            models.Partido.objects.filter(
                etapa__nombre='foo',
                fecha='2018-07-11 09:15-03:00',
                local='AR',
                visitante='NG',
            ).exists()
        )

    def test_validar_partidos(self):
        etapa = factories.EtapaFactory()
        user = self.make_user()
        data = {
            'nombre': 'foo',
            'vencimiento': '10/07/2018 00:00',
            'publica': False,
            # managenement form
            'partidos-TOTAL_FORMS': 5,
            'partidos-INITIAL_FORMS': 0,
            # end managenement form
            'partidos-0-fecha': '11/07/2018 09:15',
            'partidos-0-local': 'AR',
            'partidos-0-visitante': 'NG',
        }
        with self.login(user):
            self.post('apuestas:update', data=data, slug=etapa.slug)
            self.response_302()
        self.assertEqual(models.Partido.objects.count(), 1)

    def test_eliminar_partidos(self):
        etapa = factories.EtapaFactory()
        partido = factories.PartidoFactory(etapa=etapa)
        user = self.make_user()
        data = {
            'nombre': 'foo',
            'vencimiento': '10/07/2018 00:00',
            'publica': False,
            # managenement form
            'partidos-TOTAL_FORMS': 1,
            'partidos-INITIAL_FORMS': 1,
            # end managenement form
            'partidos-0-DELETE': 'on',
            'partidos-0-etapa': etapa.id,
            'partidos-0-fecha': '11/07/2018 09:15',
            'partidos-0-id': partido.id,
            'partidos-0-local': 'AR',
            'partidos-0-visitante': 'NG',

        }
        with self.login(user):
            self.post('apuestas:update', data=data, slug=etapa.slug)
            self.response_302()
        self.assertEqual(models.Partido.objects.count(), 0)


class CargarResultadosView(TestCase):
    def test_get_formset(self):
        etapa = factories.EtapaFactory()
        user = self.make_user()
        with self.login(user):
            self.get('apuestas:cargar_resultados', slug=etapa.slug)
        self.assertInContext('formset')
        self.assertInContext('etapa')

    def test_no_mostrar_partidos_futuros(self):
        fecha_futura = timezone.now() + datetime.timedelta(days=1)
        partido_futuro = factories.PartidoFactory(fecha=fecha_futura)
        etapa = partido_futuro.etapa
        user = self.make_user()
        with self.login(user):
            self.get('apuestas:cargar_resultados', slug=etapa.slug)
        formset = self.context['formset']
        self.assertNotIn(partido_futuro, formset.queryset)

    def test_mostrar_partidos_pasados(self):
        partido_pasado = factories.PartidoFactory(
            fecha=timezone.now(),
            goles_local=None,
            goles_visitante=None,
        )
        etapa = partido_pasado.etapa
        user = self.make_user()
        with self.login(user):
            self.get('apuestas:cargar_resultados', slug=etapa.slug)
        formset = self.context['formset']
        self.assertIn(partido_pasado, formset.queryset)

    def test_no_mostrar_partidos_con_resultados(self):
        partido = factories.PartidoFactory(
            fecha=timezone.now(),
            goles_local=1,
            goles_visitante=1,
        )
        etapa = partido.etapa
        user = self.make_user()
        with self.login(user):
            self.get('apuestas:cargar_resultados', slug=etapa.slug)
        formset = self.context['formset']
        self.assertNotIn(partido, formset.queryset)

    def test_cargar_resultados(self):
        partido = factories.PartidoFactory(
            fecha=timezone.now(),
            goles_local=None,
            goles_visitante=None,
        )
        etapa = partido.etapa
        user = self.make_user()
        data = {
            'partidos-TOTAL_FORMS': 1,
            'partidos-INITIAL_FORMS': 1,
            'partidos-0-id': partido.id,
            'partidos-0-goles_local': 5,
            'partidos-0-goles_visitante': 3,
        }
        with self.login(user):
            self.post('apuestas:cargar_resultados', data=data, slug=etapa.slug)
        partido.refresh_from_db()
        self.assertEqual(partido.goles_local, 5)
        self.assertEqual(partido.goles_visitante, 3)


class RankingViewTests(TestCase):
    def hacer_apuestas(self):
        self.user1 = self.make_user('user1')
        self.user2 = self.make_user('user2')
        self.user3 = self.make_user('user3')
        partidos = factories.PartidoFactory.create_batch(10,
                                                         goles_local=1,
                                                         goles_visitante=0)
        for partido in partidos:
            factories.ApuestaFactory(usuario=self.user1,
                                     partido=partido,
                                     goles_local=0,
                                     goles_visitante=1,
                                     ganador=constants.EMPATE)
            factories.ApuestaFactory(usuario=self.user2,
                                     partido=partido,
                                     goles_local=1,
                                     goles_visitante=0,
                                     ganador=constants.EMPATE)
            factories.ApuestaFactory(usuario=self.user3,
                                     partido=partido,
                                     goles_local=0,
                                     goles_visitante=1,
                                     ganador=constants.GANA_LOCAL)

    def test_ranking(self):
        self.hacer_apuestas()
        with self.login(self.user1):
            self.get('apuestas:ranking')
        ranking = self.context['ranking']
        expected = [
            ('user2', 30),
            ('user3', 10),
            ('user1', 0),
        ]
        self.assertEqual(ranking, expected)

    def test_ranking_sin_apuestas(self):
        user = self.make_user()
        with self.login(user):
            self.get('apuestas:ranking')
        ranking = self.context['ranking']
        self.assertEqual(len(ranking), 0)
