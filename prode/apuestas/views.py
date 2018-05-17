from django import shortcuts
from django.views import generic
from django.contrib.auth import mixins
from django.forms import formset_factory

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
