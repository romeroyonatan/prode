from django.test import TestCase
from django.urls import (
    resolve,
    reverse,
)


class ApuestasURLSTests(TestCase):
    def test_resolve_apostar(self):
        self.assertEqual(resolve('/cuartos/apostar/').view_name,
                         'apuestas:apostar')

    def test_reverse_apostar(self):
        self.assertEqual(reverse('apuestas:apostar',
                                 kwargs={'slug': 'cuartos'}),
                         '/cuartos/apostar/')

    def test_resolve_detail(self):
        self.assertEqual(resolve('/cuartos/').view_name,
                         'apuestas:detail')

    def test_reverse_detail(self):
        self.assertEqual(reverse('apuestas:detail',
                                 kwargs={'slug': 'cuartos'}),
                         '/cuartos/')

    def test_resolve_create(self):
        self.assertEqual(resolve('/etapas/crear/').view_name,
                         'apuestas:create')

    def test_reverse_create(self):
        self.assertEqual(reverse('apuestas:create'), '/etapas/crear/')

    def test_resolve_update(self):
        self.assertEqual(resolve('/cuartos/editar/').view_name,
                         'apuestas:update')

    def test_reverse_update(self):
        self.assertEqual(reverse('apuestas:update',
                                 kwargs={'slug': 'cuartos'}),
                         '/cuartos/editar/')

    def test_resolve_cargar_resultados(self):
        self.assertEqual(
            resolve('/cuartos/cargar-resultados/').view_name,
            'apuestas:cargar_resultados'
        )

    def test_reverse_cargar_resultados(self):
        self.assertEqual(
            reverse('apuestas:cargar_resultados', kwargs={'slug': 'cuartos'}),
            '/cuartos/cargar-resultados/'
        )

    def test_resolve_ranking(self):
        self.assertEqual(
            resolve('/ranking/').view_name, 'apuestas:ranking'
        )

    def test_reverse_ranking(self):
        self.assertEqual(
            reverse('apuestas:ranking'), '/ranking/'
        )
