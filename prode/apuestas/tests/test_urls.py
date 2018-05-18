from django.test import TestCase
from django.urls import (
    resolve,
    reverse,
)


class ApuestasURLSTests(TestCase):
    def test_resolve_editar(self):
        self.assertEqual(resolve('/apuestas/etapas/cuartos/editar/').view_name,
                         'apuestas:editar')

    def test_reverse_editar(self):
        self.assertEqual(reverse('apuestas:editar',
                                 kwargs={'slug': 'cuartos'}),
                         '/apuestas/etapas/cuartos/editar/')

    def test_resolve_detail(self):
        self.assertEqual(resolve('/apuestas/etapas/cuartos/').view_name,
                         'apuestas:detail')

    def test_reverse_detail(self):
        self.assertEqual(reverse('apuestas:detail',
                                 kwargs={'slug': 'cuartos'}),
                         '/apuestas/etapas/cuartos/')
