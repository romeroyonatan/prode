from django.test import TestCase
from django.urls import (
    resolve,
    reverse,
)


class ApuestasURLSTests(TestCase):
    def test_resolve_editar(self):
        self.assertEqual(resolve('/apuestas/cuartos/editar/').view_name,
                         'apuestas:editar')

    def test_reverse_editar(self):
        self.assertEqual(reverse('apuestas:editar',
                                 kwargs={'slug': 'cuartos'}),
                         '/apuestas/cuartos/editar/')
