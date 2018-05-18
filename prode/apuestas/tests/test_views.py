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
            response = self.get('apuestas:editar', slug=etapa.slug)
        self.assertIn('formset', response.context)
        self.assertIn('etapa', response.context)

    def test_get_form_kwargs(self):
        etapa = factories.EtapaFactory()
        user = self.make_user()
        with self.login(user):
            self.get('apuestas:editar', slug=etapa.slug)
        view = self.context['view']
        kwargs = view.get_form_kwargs()
        self.assertEqual(kwargs['usuario'], user)
        self.assertEqual(kwargs['etapa'], etapa)

    def test_get_form_class(self):
        etapa = factories.EtapaFactory()
        user = self.make_user()
        with self.login(user):
            self.get('apuestas:editar', slug=etapa.slug)
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
            self.post('apuestas:editar', data=data, slug=etapa.slug)
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
