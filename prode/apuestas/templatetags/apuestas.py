from django import template

from prode.apuestas import models

register = template.Library()

@register.simple_tag
def get_etapas(current_user):
    """Obtiene las etapas que puede ver el usuario actual.

    Si es un usuario no autenticado, no podra ver etapas
    Si es un usuario normal, solo podra ver las etapas publicas
    Si es un usuario con permisos para editar etapas, podra ver las etapas no
    publicas
    """
    queryset = models.Etapa.objects.all()
    if current_user.is_anonymous:
        return queryset.none()
    if not current_user.has_perm('apuestas.change_etapa'):
        return queryset.filter(publica=True)
    return queryset
