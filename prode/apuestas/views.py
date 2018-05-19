from django import shortcuts
from django.views import generic
from django.contrib.auth import mixins
from django.forms import (
    formset_factory,
    modelformset_factory,
    inlineformset_factory,
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
        return shortcuts.redirect('apuestas:apostar', slug=self.object.slug)


class EtapaDetailView(mixins.LoginRequiredMixin, generic.DetailView):
    model = models.Etapa

    def get_context_data(self, **kwargs):
        """Agrega ganador al contexto."""
        kwargs['puntajes'] = self.get_puntajes()
        return super().get_context_data(**kwargs)

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.prefetch_related('partidos__apuestas__usuario')

    def get_puntajes(self):
        puntajes = models.Apuesta.objects.get_puntajes(etapa=self.object)
        # obtengo los 5 primeros
        return puntajes[:5]


class EtapaCreateView(mixins.LoginRequiredMixin,
                      generic.CreateView):
    """Permite crear una etapa nueva"""
    model = models.Etapa
    form_class = forms.EtapaForm
    # TODO permisos

    def get_context_data(self, **kwargs):
        """Agrega formset al contexto."""
        kwargs['partidos_formset'] = self.get_partidos_formset()
        return super().get_context_data(**kwargs)

    def get_partidos_formset(self):
        """Obtiene formset para crear partidos"""
        PartidoFormset = modelformset_factory(models.Partido,
                                              forms.PartidoForm,
                                              extra=3)
        if self.request.method == 'POST':
            return PartidoFormset(self.request.POST, prefix='partidos')
        return PartidoFormset(prefix='partidos')

    def form_valid(self, form):
        """Guarda etapa y los partidos asociados."""
        etapa = form.save()
        print(vars(etapa))
        formset = self.get_partidos_formset()
        if formset.is_valid():
            self.guardar_partidos(formset, etapa)
        return shortcuts.redirect('apuestas:update', slug=etapa.slug)

    def guardar_partidos(self, formset, etapa):
        """Guarda el formulario de partido"""
        partidos = formset.save(commit=False)
        for partido in partidos:
            partido.etapa = etapa
            partido.save()


class EtapaUpdateView(mixins.LoginRequiredMixin,
                      generic.UpdateView):
    """Permite editar una etapa"""
    model = models.Etapa
    form_class = forms.EtapaForm
    # TODO permisos

    def get_context_data(self, **kwargs):
        """Agrega formset al contexto."""
        kwargs['partidos_formset'] = self.get_partidos_formset()
        return super().get_context_data(**kwargs)

    def get_partidos_formset(self):
        """Obtiene formset para crear partidos. Utiliza inlineformset ya que
        asocia los partidos a la etapa automaticamente.
        """
        PartidoFormset = inlineformset_factory(
            models.Etapa,
            models.Partido,
            forms.PartidoForm,
            extra=0,
        )
        if self.request.method == 'POST':
            return PartidoFormset(self.request.POST,
                                  instance=self.get_object())
        return PartidoFormset(instance=self.get_object())

    def form_valid(self, form):
        """Guarda etapa y los partidos asociados."""
        etapa = form.save()
        formset = self.get_partidos_formset()
        if formset.is_valid():
            formset.save()
        return shortcuts.redirect('apuestas:update', slug=etapa.slug)
