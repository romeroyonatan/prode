from test_plus.test import TestCase

from prode.apuestas.tests import factories


class TestUser(TestCase):

    def setUp(self):
        self.user = self.make_user()

    def test__str__(self):
        self.assertEqual(
            self.user.__str__(),
            "testuser",  # This is the default username for self.make_user()
        )

    def test_get_absolute_url(self):
        self.assertEqual(self.user.get_absolute_url(), "/users/testuser/")

    def test_get_puntaje(self):
        apuestas = factories.ApuestaFactory.create_batch(10, usuario=self.user)
        puntaje = sum(apuesta.puntaje for apuesta in apuestas)
        self.assertEqual(self.user.get_puntaje(), puntaje)

    def test_get_puntaje_partidos_sin_definir(self):
        factories.ApuestaFactory.create_batch(
            10,
            usuario=self.user,
            partido__goles_local=None,
            partido__goles_visitante=None,
        )
        self.assertEqual(self.user.get_puntaje(), 0)
