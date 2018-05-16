from django.test import RequestFactory
from test_plus.test import TestCase

from prode.apuestas import views

from . import factories

class AdministrarApuestasTests(TestCase):
    def test_formset_in_context(self):
        etapa = factories.EtapaFactory()
        factories.PartidoFactory(etapa=etapa)
        user = self.make_user()
        with self.login(user):
            response = self.get('apuestas:editar', slug=etapa.slug)
        self.assertIn('formset', response.context)
