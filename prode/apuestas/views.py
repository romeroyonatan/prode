from django import shortcuts
from django.contrib.auth.decorators import login_required
from django.forms import formset_factory

from . import (
    forms,
    models,
)


@login_required
def administrar_apuestas(request, slug):
    """Permite administrar las apuestas.

    Mientras la etapa no este cerrada permite crear y editar las apuestas
    del usuario.
    """
    etapa = shortcuts.get_object_or_404(models.Etapa, slug=slug)
    ApuestaFormSet = formset_factory(forms.ApuestaForm,
                                     formset=forms.ApuestaBaseFormSet,
                                     min_num=etapa.partidos.count(),
                                     max_num=etapa.partidos.count(),
                                     extra=0)
    if request.method == 'POST':
        formset = ApuestaFormSet(request.POST,
                                 usuario=request.user,
                                 etapa=etapa)
        if formset.is_valid():
            # guardar apuestas
            for form in formset:
                form.save()
    else:
        formset = ApuestaFormSet(usuario=request.user, etapa=etapa)
    return shortcuts.render(request,
                            'apuestas/apuestas_form.html',
                            {'formset': formset})
