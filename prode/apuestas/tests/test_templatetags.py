from django.contrib.auth.models import AnonymousUser

from test_plus import TestCase

from prode.apuestas.templatetags import apuestas

from . import factories


class GetEtapaTests(TestCase):
    def test_anonymous_user(self):
        factories.EtapaFactory(publica=True)
        self.assertFalse(apuestas.get_etapas(AnonymousUser()))

    def test_normal_user(self):
        user = self.make_user()
        publica = factories.EtapaFactory(publica=True)
        no_publica = factories.EtapaFactory(publica=False)
        etapas = apuestas.get_etapas(user)
        self.assertIn(publica, etapas)
        self.assertNotIn(no_publica, etapas)

    def test_usuario_con_permisos_cambiar_etapa(self):
        user = self.make_user(perms=('apuestas.change_etapa',))
        publica = factories.EtapaFactory(publica=True)
        no_publica = factories.EtapaFactory(publica=False)
        etapas = apuestas.get_etapas(user)
        self.assertIn(publica, etapas)
        self.assertIn(no_publica, etapas)
