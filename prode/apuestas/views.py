import itertools

from django import shortcuts
from django.db.models import (
    Case,
    F,
    PositiveSmallIntegerField,
    Value,
    When,
)
from django.views import generic
from django.contrib.auth import mixins
from django.forms import formset_factory

from prode.apuestas.models import (
    GANA_LOCAL,
    GANA_VISITANTE,
    EMPATE
)

from . import (
    forms,
    models,
)


class AdministrarApuestasFormView(mixins.LoginRequiredMixin,
                                  generic.edit.SingleObjectMixin,
                                  generic.FormView):
    """Permite administrar las apuestas.

    Mientras la etapa no este cerrada permite crear y editar las apuestas
    del usuario.
    """
    template_name = 'apuestas/apuestas_form.html'
    model = models.Etapa
    object = None

    def get_form_class(self):
        """Obtiene la clase del formulario a traves del factory de formset."""
        self.object = self.get_object()
        cantidad_partidos = self.object.partidos.count()
        return formset_factory(forms.ApuestaForm,
                               formset=forms.ApuestaBaseFormSet,
                               min_num=cantidad_partidos,
                               max_num=cantidad_partidos,
                               extra=0)

    def get_form_kwargs(self):
        """Obtiene los parametros que se le pasaran al contructor del
        formset."""
        kwargs = super().get_form_kwargs()
        kwargs['usuario'] = self.request.user
        kwargs['etapa'] = self.object
        return kwargs

    def get_context_data(self, **kwargs):
        """Agrega formset al contexto"""
        kwargs['formset'] = self.get_form()
        return super().get_context_data(**kwargs)

    def form_valid(self, form):
        """Guarda los formularios del formset"""
        # alias para que quede claro que estoy trabajando con un formset
        formset = form
        for _form in formset:
            _form.save()
        return shortcuts.redirect('apuestas:editar', slug=self.object.slug)


class EtapaDetailView(mixins.LoginRequiredMixin, generic.DetailView):
    model = models.Etapa

    def get_context_data(self, **kwargs):
        """Agrega ganador al contexto."""
        kwargs['puntajes'] = self.get_puntajes_()
        return super().get_context_data(**kwargs)

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.prefetch_related('partidos__apuestas__usuario')

    def get_puntajes_(self):
        queryset = (
            models
            .Apuesta
            .objects
            .filter(partido__etapa__slug=self.kwargs['slug'])
            .annotate(
                # Logica del puntaje
                puntos_ganador=Case(
                    When(ganador=GANA_LOCAL,
                         partido__goles_local__gt=F('partido__goles_visitante'),
                         then=Value(1)),
                    When(ganador=GANA_VISITANTE,
                         partido__goles_visitante__gt=F('partido__goles_local'),
                         then=Value(1)),
                    When(ganador=EMPATE,
                         partido__goles_visitante=F('partido__goles_local'),
                         then=Value(1)),
                    default=0,
                    output_field=PositiveSmallIntegerField(),
                ),
                puntos_goles=Case(
                    When(goles_local=F('partido__goles_local'),
                         goles_visitante=F('partido__goles_visitante'),
                         then=Value(3)),
                    default=0,
                    output_field=PositiveSmallIntegerField(),
                ),
            )
            .annotate(puntos=F('puntos_goles') + F('puntos_ganador'))
            .values_list('usuario__username', 'puntos')
        )
        # obtengo puntajes sumados por usuario
        puntajes_sumados = [
            (user, sum(puntos for _, puntos in group))
            for user, group in itertools.groupby(queryset, key=lambda x: x[0])
        ]
        # ordeno por cantidad de puntos descendente
        puntajes = sorted(puntajes_sumados, key=lambda x: -x[1])
        # obtengo los 5 primeros
        return puntajes[:5]
