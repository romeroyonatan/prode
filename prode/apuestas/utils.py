from . import models


def get_ranking(usuario):
    """Obtiene el puesto en el ranking del usuario pasado por parametro.

    :returns: int o None si no se encontro el usuario
    """
    ranking = models.Apuesta.objects.ranking()
    for puesto, (username, _) in enumerate(ranking):
        if username == usuario.username:
            return puesto + 1
    return None
