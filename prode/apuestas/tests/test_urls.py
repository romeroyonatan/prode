from django.test import TestCase
from django.urls import (
    resolve,
    reverse,
)


class ApuestasURLSTests(TestCase):
    def test_resolve_apostar(self):
        self.assertEqual(resolve('/apuestas/etapas/cuartos/apostar/').view_name,
                         'apuestas:apostar')

    def test_reverse_apostar(self):
        self.assertEqual(reverse('apuestas:apostar',
                                 kwargs={'slug': 'cuartos'}),
                         '/apuestas/etapas/cuartos/apostar/')

    def test_resolve_detail(self):
        self.assertEqual(resolve('/apuestas/etapas/cuartos/').view_name,
                         'apuestas:detail')

    def test_reverse_detail(self):
        self.assertEqual(reverse('apuestas:detail',
                                 kwargs={'slug': 'cuartos'}),
                         '/apuestas/etapas/cuartos/')

    def test_resolve_create(self):
        self.assertEqual(resolve('/apuestas/etapas/crear/').view_name,
                         'apuestas:create')

    def test_reverse_create(self):
        self.assertEqual(reverse('apuestas:create'), '/apuestas/etapas/crear/')

    def test_resolve_update(self):
        self.assertEqual(resolve('/apuestas/etapas/cuartos/editar/').view_name,
                         'apuestas:update')

    def test_reverse_update(self):
        self.assertEqual(reverse('apuestas:update',
                                 kwargs={'slug': 'cuartos'}),
                         '/apuestas/etapas/cuartos/editar/')

    def test_resolve_cargar_resultados(self):
        self.assertEqual(
            resolve('/apuestas/etapas/cuartos/cargar-resultados/').view_name,
            'apuestas:cargar_resultados'
        )

    def test_reverse_cargar_resultados(self):
        self.assertEqual(
            reverse('apuestas:cargar_resultados', kwargs={'slug': 'cuartos'}),
            '/apuestas/etapas/cuartos/cargar-resultados/'
        )

    def test_resolve_ranking(self):
        self.assertEqual(
            resolve('/apuestas/ranking/').view_name, 'apuestas:ranking'
        )

    def test_reverse_ranking(self):
        self.assertEqual(
            reverse('apuestas:ranking'), '/apuestas/ranking/'
        )
