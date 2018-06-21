import itertools
import functools
from datetime import timedelta

from django import shortcuts
from django.contrib import messages
from django.contrib.auth import mixins
from django.forms import (
    formset_factory,
    modelformset_factory,
    inlineformset_factory,
)
from django.utils import timezone
from django.views import generic

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

    def dispatch(self, *args, **kwargs):
        """Si la etapa esta vencida, no se puede apostar mas. Redirige al
        detalle de la etapa.
        """
        etapa = self.get_object()
        if etapa.vencida:
            return shortcuts.redirect(etapa)
        return super().dispatch(*args, **kwargs)

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
        messages.success(self.request, '''La apuesta fue guardada con éxito,
                         puede seguir editandola hasta que se acabe el tiempo
                         para apostar''')
        return shortcuts.redirect('apuestas:apostar', slug=self.object.slug)


class EtapaDetailView(mixins.LoginRequiredMixin, generic.DetailView):
    """Permite ver todas las apuestas de todos los partidos de la etapa.

    Ademas muestra los mejores 5 apostadores de la etapa con su puntaje

    Solo se permite ver los detalles de la etapa cuando la etapa este
    vencida.
    """
    model = models.Etapa

    def dispatch(self, *args, **kwargs):
        """Si la etapa no esta vencida, no se puede ver las apuestas de otros
        apostadores. Redirige a la pantalla de apostar.
        """
        etapa = self.get_object()
        if not etapa.vencida:
            return shortcuts.redirect('apuestas:apostar', slug=etapa.slug)
        return super().dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):
        """Agrega ganador al contexto."""
        kwargs['puntajes'] = self.get_puntajes()
        return super().get_context_data(**kwargs)

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.prefetch_related('partidos__apuestas__usuario')

    def get_puntajes(self):
        puntajes = models.Apuesta.objects.get_puntajes(etapa=self.object)
        # obtengo los 10 primeros
        return puntajes[:10]


class EtapaCreateView(mixins.PermissionRequiredMixin,
                      generic.CreateView):
    """Permite crear una etapa nueva.

    Requiere permisos ``apuestas.add_etapa``.
    """
    model = models.Etapa
    form_class = forms.EtapaForm
    permission_required = 'apuestas.add_etapa'

    def get_context_data(self, **kwargs):
        """Agrega formset al contexto."""
        kwargs['partidos_formset'] = self.get_partidos_formset()
        return super().get_context_data(**kwargs)

    def get_partidos_formset(self):
        """Obtiene formset para crear partidos"""
        queryset = models.Partido.objects.none()
        PartidoFormset = modelformset_factory(models.Partido,
                                              forms.PartidoForm,
                                              extra=3)
        if self.request.method == 'POST':
            return PartidoFormset(self.request.POST,
                                  prefix='partidos',
                                  queryset=queryset)
        return PartidoFormset(prefix='partidos', queryset=queryset)

    def form_valid(self, form):
        """Guarda etapa y los partidos asociados."""
        etapa = form.save()
        formset = self.get_partidos_formset()
        if formset.is_valid():
            partidos = formset.save(commit=False)
            for partido in partidos:
                partido.etapa = etapa
                partido.save()
        messages.success(self.request, '''La etapa fue guardada con éxito.
                         Podrá seguir editando la etapa hasta que la misma sea
                         marcada como pública''')
        return shortcuts.redirect('apuestas:update', slug=etapa.slug)


class EtapaUpdateView(mixins.UserPassesTestMixin,
                      generic.UpdateView):
    """Permite editar una etapa.

    Se pueden editar etapas que no sean publicas con el permiso
    ``apuestas.change_etapa``. Si la etapa es publica, solo un
    superadministrador puede cambiarla.
    """
    model = models.Etapa
    form_class = forms.EtapaForm

    def test_func(self):
        """Si la etapa es publica, solo un administrador puede editarla"""
        etapa = self.get_object()
        if etapa.publica:
            return self.request.user.is_superuser
        return self.request.user.has_perm('apuestas.change_etapa')

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
        messages.success(self.request, '''La etapa fue guardada con éxito.
                         Podrá seguir editando la etapa hasta que la misma sea
                         marcada como pública''')
        return shortcuts.redirect('apuestas:update', slug=etapa.slug)


class CargarResultadosView(mixins.PermissionRequiredMixin,
                           generic.edit.SingleObjectMixin,
                           generic.FormView):
    """Permite cargas los resultados de los partidos pasados.

    Requiere permisos ``apuestas.change_etapa``

    No permite editar los resultados de partidos pasados, excepto para el admin
    en caso de correcciones
    """
    model = models.Etapa
    template_name = 'apuestas/cargar_resultados.html'
    prefix = 'partidos'
    object = None
    permission_required = 'apuestas.change_etapa'

    def get_form_class(self):
        """Obtiene formset para cargar los resultados."""
        return modelformset_factory(
            models.Partido,
            forms.CargarResultadosForm,
            extra=0,
        )

    def get_context_data(self, **kwargs):
        """Agrega etapa y formset al contexto"""
        self.object = self.get_object()
        kwargs['etapa'] = self.object
        kwargs['formset'] = self.get_form()
        return super().get_context_data(**kwargs)

    def get_form_kwargs(self):
        """Obtiene los argumentos con los que creara la instancia del formset.
        """
        kwargs = super().get_form_kwargs()
        kwargs['queryset'] = self.get_partidos_queryset()
        return kwargs

    def get_partidos_queryset(self):
        """Obtiene el queryset de partidos que van a ser editados.

        Solamente se va a poder cargar los resultados de los partidos pasados
        que no tengan resultado cargado (es decir que `goles_local` y
        `goles_visitante` sea None.
        """
        etapa = self.get_object()
        # Selecciono partidos que hayan terminado (se calcula mas o menos 2
        # horas de duracion por partido)
        terminado = timezone.now() - timedelta(hours=2)
        # El admin puede editar resultados de partidos pasados
        if self.request.user.is_superuser:
            return etapa.partidos.filter(fecha__lt=terminado)
        return etapa.partidos.filter(
            fecha__lt=terminado,
            goles_local__isnull=True,
            goles_visitante__isnull=True,
        )

    def form_valid(self, form):
        """Guarda formulario y redirije a detalles de la etapa."""
        form.save()
        messages.success(self.request, '''Los resultados se han guardado. No
                         podrá editarlos en el futuro''')
        return shortcuts.redirect('apuestas:detail', slug=self.kwargs['slug'])


class RankingView(mixins.LoginRequiredMixin, generic.ListView):
    """Permite ver el ranking de mejores apostadores de todas las etapas"""
    template_name = 'apuestas/ranking.html'
    context_object_name = 'ranking'

    @functools.lru_cache()
    def get_queryset(self):
        """Obtiene ranking de mejores apostadores.

        :returns: Lista de tuplas (nombre de usuario, puntaje)
        """
        return models.Apuesta.objects.ranking()

    def get_context_data(self, **kwargs):
        kwargs['ganadores'] = self.get_ganadores()
        kwargs['puesto_actual'] = self.get_puesto_actual()
        return super().get_context_data(**kwargs)

    def get_ganadores(self):
        """Obtiene una tupla con los nombres de usuario de ganadores.

        En caso que no haya apuestas, devuelve una tupla vacia
        """
        ranking = self.get_queryset()
        if not ranking:
            return tuple()
        mayor_puntaje = ranking[0].puntos
        ganadores = itertools.takewhile(lambda x: x.puntos == mayor_puntaje,
                                        ranking)
        return tuple(ganador.username for ganador in ganadores)

    def get_puesto_actual(self):
        """Obtiene el puesto actual del usuario en sesion

        :returns: Numero de puesto del usuario o None si no se encontro
        """
        return self.request.user.ranking
