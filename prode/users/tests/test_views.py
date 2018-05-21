import datetime

from django.utils import timezone
from django.test import RequestFactory

from test_plus.test import TestCase

from prode.apuestas.tests import factories
from prode.apuestas import constants

from ..views import UserRedirectView, UserUpdateView


class BaseUserTestCase(TestCase):

    def setUp(self):
        self.user = self.make_user()
        self.factory = RequestFactory()


class TestUserRedirectView(BaseUserTestCase):

    def test_get_redirect_url(self):
        # Instantiate the view directly. Never do this outside a test!
        view = UserRedirectView()
        # Generate a fake request
        request = self.factory.get("/fake-url")
        # Attach the user to the request
        request.user = self.user
        # Attach the request to the view
        view.request = request
        # Expect: '/usuarios/testuser/', as that is the default username for
        #   self.make_user()
        self.assertEqual(view.get_redirect_url(), '/usuarios/testuser/')

    def test_get_redirect_url__etapa_publica(self):
        etapa = factories.EtapaFactory(publica=True, slug='foo')
        # Instantiate the view directly. Never do this outside a test!
        view = UserRedirectView()
        # Generate a fake request
        request = self.factory.get("/fake-url")
        # Attach the user to the request
        request.user = self.user
        # Attach the request to the view
        view.request = request
        self.assertEqual(view.get_redirect_url(), '/foo/apostar/')


class TestUserUpdateView(BaseUserTestCase):

    def setUp(self):
        # call BaseUserTestCase.setUp()
        super(TestUserUpdateView, self).setUp()
        # Instantiate the view directly. Never do this outside a test!
        self.view = UserUpdateView()
        # Generate a fake request
        request = self.factory.get("/fake-url")
        # Attach the user to the request
        request.user = self.user
        # Attach the request to the view
        self.view.request = request

    def test_get_success_url(self):
        # Expect: '/usuarios/testuser/', as that is the default username for
        #   self.make_user()
        self.assertEqual(self.view.get_success_url(), "/usuarios/testuser/")

    def test_get_object(self):
        # Expect: self.user, as that is the request's user object
        self.assertEqual(self.view.get_object(), self.user)


class TestUserDetailView(BaseUserTestCase):
    def test_get_etapas_apostadas(self):
        # Creo 10 apuestas, en 10 etapas distintas, con 4 puntos en cada una
        apuestas = factories.ApuestaFactory.create_batch(
            10,
            partido__etapa__vencimiento=timezone.now(),
            usuario=self.user,
            partido__goles_local=1,
            partido__goles_visitante=0,
            goles_local=1,
            goles_visitante=0,
            ganador=constants.GANA_LOCAL,
        )
        with self.login(self.user):
            self.get('users:detail', username=self.user.username)
        # obtengo etapas apostadas
        actual = self.context['etapas_apostadas']
        for i, apuesta in enumerate(apuestas):
            self.assertEqual(actual[i].etapa, apuesta.partido.etapa)
            self.assertEqual(actual[i].puntos, 4)

    def test_no_mostrar_etapas_sin_vencer(self):
        """No muestro apuestas de etapas que siguen activas"""
        # Creo apuesta con vencimiento de etapa en el futuro
        fecha_futura = timezone.now() + datetime.timedelta(days=1)
        factories.ApuestaFactory(
            usuario=self.user,
            partido__etapa__vencimiento=fecha_futura,
            partido__goles_local=1,
            partido__goles_visitante=0,
            goles_local=1,
            goles_visitante=0,
            ganador=constants.GANA_LOCAL,
        )
        with self.login(self.user):
            self.get('users:detail', username=self.user.username)
        # obtengo etapas apostadas
        actual = self.context['etapas_apostadas']
        self.assertEqual(len(actual), 0)
