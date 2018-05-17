from test_plus.test import TestCase

from prode.apuestas import (
    forms,
    models,
)

from . import factories


class ApuestaFormTests(TestCase):
    def test_init(self):
        user = self.make_user()
        partido = factories.PartidoFactory.build()
        form = forms.ApuestaForm(usuario=user, partido=partido)
        self.assertEqual(form.usuario, user)
        self.assertEqual(form.partido, partido)

    def test_adaptar_labels(self):
        user = self.make_user()
        partido = factories.PartidoFactory.build(
            local='AR',
            visitante='BR',
        )
        form = forms.ApuestaForm(usuario=user, partido=partido)
        choices = form.fields['ganador'].choices
        self.assertEqual(choices[1][1], 'Gana Argentina')
        self.assertEqual(choices[2][1], 'Gana Brazil')
        self.assertEqual(form.fields['goles_local'].label, 'Argentina')
        self.assertEqual(form.fields['goles_visitante'].label, 'Brazil')

    def test_save(self):
        user = self.make_user()
        partido = factories.PartidoFactory(
            local='AR',
            visitante='BR',
        )
        data = {'ganador': models.GANA_LOCAL,
                'goles_local': 2,
                'goles_visitante': 1}
        form = forms.ApuestaForm(usuario=user, partido=partido, data=data)
        apuesta = form.save()
        self.assertEqual(apuesta.partido, partido)
        self.assertEqual(apuesta.usuario, user)
        self.assertEqual(apuesta.ganador, models.GANA_LOCAL)
        self.assertEqual(apuesta.goles_local, 2)
        self.assertEqual(apuesta.goles_visitante, 1)


class ApuestaBaseFormSet(TestCase):
    def test_init(self):
        user = self.make_user()
        etapa = factories.EtapaFactory.build()
        form = forms.ApuestaBaseFormSet(usuario=user, etapa=etapa)
        self.assertEqual(form.usuario, user)
        self.assertEqual(form.etapa, etapa)

    def test_get_form_kwargs(self):
        user = self.make_user()
        etapa = factories.EtapaFactory()
        partido = factories.PartidoFactory(etapa=etapa)
        form = forms.ApuestaBaseFormSet(usuario=user, etapa=etapa)
        kwargs = form.get_form_kwargs(0)
        self.assertEqual(kwargs['usuario'], user)
        self.assertEqual(kwargs['partido'], partido)
        self.assertIsNone(kwargs['instance'])

    def test_get_form_kwargs_apuesta_existente(self):
        user = self.make_user()
        etapa = factories.EtapaFactory()
        partido = factories.PartidoFactory(etapa=etapa)
        apuesta = factories.ApuestaFactory(partido=partido)
        form = forms.ApuestaBaseFormSet(usuario=user, etapa=etapa)
        kwargs = form.get_form_kwargs(0)
        self.assertEqual(kwargs['usuario'], user)
        self.assertEqual(kwargs['partido'], partido)
        self.assertIsNone(kwargs['instance'], apuesta)

    def test_get_form_kwargs_index_none(self):
        user = self.make_user()
        etapa = factories.EtapaFactory()
        factories.PartidoFactory(etapa=etapa)
        form = forms.ApuestaBaseFormSet(usuario=user, etapa=etapa)
        kwargs = form.get_form_kwargs(None)
        self.assertEqual(kwargs['usuario'], user)
        self.assertNotIn('partido', kwargs)
        self.assertNotIn('instance', kwargs)

    def test_get_apuesta(self):
        user = self.make_user()
        apuesta = factories.ApuestaFactory(usuario=user)
        partido = apuesta.partido
        etapa = partido.etapa
        form = forms.ApuestaBaseFormSet(usuario=user, etapa=etapa)
        self.assertEqual(form.get_apuesta(partido), apuesta)

    def test_get_apuesta_inexistente(self):
        user = self.make_user()
        partido = factories.PartidoFactory()
        etapa = partido.etapa
        form = forms.ApuestaBaseFormSet(usuario=user, etapa=etapa)
        self.assertIsNone(form.get_apuesta(partido))

    def test_get_apuesta_otro_usuario(self):
        user = self.make_user()
        user1 = self.make_user(username='user1')
        # creo apuesta de otro usuario
        factories.ApuestaFactory(usuario=user1)
        partido = factories.PartidoFactory()
        etapa = partido.etapa
        form = forms.ApuestaBaseFormSet(usuario=user, etapa=etapa)
        self.assertIsNone(form.get_apuesta(partido))
