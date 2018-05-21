from test_plus import TestCase

from prode.apuestas import (
    constants,
    utils,
)

from . import factories

class UtilsTests(TestCase):
    def hacer_apuestas(self):
        """Hace apuestas

        Usuario           Puntos
        self.user2        40
        self.user3        10
        self.user1        0
        """
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

    def test_get_ranking(self):
        self.hacer_apuestas()
        self.assertEqual(utils.get_ranking(self.user2), 1)
        self.assertEqual(utils.get_ranking(self.user3), 2)
        self.assertEqual(utils.get_ranking(self.user1), 3)
