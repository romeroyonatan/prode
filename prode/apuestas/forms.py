from django import forms

from . import (
    constants,
    models,
)


class ApuestaForm(forms.ModelForm):
    class Meta:
        model = models.Apuesta
        fields = ('ganador', 'goles_local', 'goles_visitante')

    def __init__(self, *args, **kwargs):
        """Guarda atributos ``usuario`` y ``partido``."""
        self.usuario = kwargs.pop('usuario')
        self.partido = kwargs.pop('partido')
        super().__init__(*args, **kwargs)
        self.adaptar_labels()

    def adaptar_labels(self):
        """Adapta los labels a cada equipo que juega el partido.

        En vez de mostrar `local` o `visitante` muestra el nombre del pais
        """
        local = self.partido.local.name
        visitante = self.partido.visitante.name
        # cambio choices del ganador
        self.fields['ganador'].choices = (
            (constants.EMPATE, 'Empate'),
            (constants.GANA_LOCAL, f'Gana {local}'),
            (constants.GANA_VISITANTE, f'Gana {visitante}'),
        )
        # cambio labels de goles
        self.fields['goles_local'].label = local
        self.fields['goles_visitante'].label = visitante

    def save(self, commit=True):
        """Guarda apuesta. Asocia partido y usuario pasado por constructor"""
        apuesta = super().save(commit=False)
        apuesta.partido = self.partido
        apuesta.usuario = self.usuario
        if commit:
            apuesta.save()
        return apuesta


class ApuestaBaseFormSet(forms.BaseFormSet):
    """Clase base de los formset generados por formset_factory."""

    def __init__(self, *args, **kwargs):
        """Guarda atributos ``usuario`` y ``etapa``"""
        self.usuario = kwargs.pop('usuario')
        self.etapa = kwargs.pop('etapa')
        self.partidos = self.etapa.partidos.all().order_by('id')
        super().__init__(*args, **kwargs)

    def get_form_kwargs(self, index):
        """Obtiene diccionario de parametros que seran pasado a cada form."""
        kwargs = super().get_form_kwargs(index)
        kwargs['usuario'] = self.usuario
        if index is not None:
            partido = self.partidos[index]
            kwargs['partido'] = partido
            kwargs['instance'] = self.get_apuesta(partido)
        return kwargs

    def get_apuesta(self, partido):
        """Obtiene apuesta asociada al partido hecha por el usuario.

	:returns: ``Apuesta`` o None
        """
        apuesta = partido.apuestas.filter(usuario=self.usuario)
        if not apuesta.exists():
            return None
        return apuesta.get()


class EtapaForm(forms.ModelForm):
    class Meta:
        model = models.Etapa
        fields = ('publica', 'nombre', 'vencimiento', 'slug')


class PartidoForm(forms.ModelForm):
    class Meta:
        model = models.Partido
        fields = ('fecha', 'local', 'visitante')
