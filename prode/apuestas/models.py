from django import urls
from django.conf import settings
from django.db import models
from django.utils import timezone

from django_countries.fields import CountryField

from . import (
    constants,
    managers,
)


class Etapa(models.Model):
    """Define una etapa en la que se puede apostar.

    Las etapas permiten definir en que tiempo se permiten apuestas y cuando
    se cierra las apuestas para empezar a cargar los resultados de los partidos

    El tiempo en el que se puede apostar esta definido por el atributo
    ``vencimiento``.
    """
    nombre = models.CharField(max_length=255,
                              help_text="Por ejemplo 'Fase de grupos'")
    vencimiento = models.DateTimeField(help_text="""Fecha-hora hasta que será
    permitido apostar. Idealmente debe ser antes que empiece el primer partido
    de la etapa. [dd/mm/aaaa hh:mm]""")
    slug = models.SlugField(
        help_text="""Texto que se mostrara en la url, por
    ejemplo si el slug fuera 'fase-de-grupos' la URL sería
    '/apuestas/etapas/fase-de-grupos/'""",
        unique=True
    )
    # define en que momento la etapa esta lista para ser presentada a los
    # usuarios para apostar
    publica = models.BooleanField(help_text="""
    Tildar cuando la etapa este lista para ser mostrada a los apostadores para
    que empiecen a apostar""")

    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        get_latest_by = 'created'
        ordering = ('created',)

    def __str__(self):
        return f'{self.nombre}'

    def get_absolute_url(self):
        """Devuelve url de la etapa:

        Si esta vencida, muestra todas las apuestas de la etapa
        Si no es publica, muestra el formulario de edicion
        Si no esta vencida, muestra el formulario de apostar.
        """
        if not self.publica:
            return urls.reverse('apuestas:update', kwargs={'slug': self.slug})
        if self.vencida:
            return urls.reverse('apuestas:detail', kwargs={'slug': self.slug})
        return urls.reverse('apuestas:apostar', kwargs={'slug': self.slug})

    @property
    def vencida(self):
        """Devuelve verdadero si la etapa esta vencida"""
        return timezone.now() > self.vencimiento


class Partido(models.Model):
    """Define un partido del fixture."""
    etapa = models.ForeignKey(Etapa,
                              null=True,
                              related_name='partidos',
                              on_delete=models.SET_NULL)
    # estos campos se definen cuando se crea la etapa
    fecha = models.DateTimeField(
        blank=True,
        null=True,
        help_text="""Fecha y hora en la que se juega el partido
        [dd/mm/aaaa hh:mm]""",
    )
    local = CountryField(blank=False, null=False)
    visitante = CountryField(blank=False, null=False)
    # estos campos se definen cuando la etapa esta cerrada
    goles_local = models.PositiveSmallIntegerField(null=True)
    goles_visitante = models.PositiveSmallIntegerField(null=True)

    def terminado(self):
        """Se asume partido terminado cuando se cargan los resultados."""
        return (self.goles_local is not None and
                self.goles_visitante is not None)

    @property
    def resultado(self):
        """Devuelve si gano local, visitante o si fue empate."""
        # no esta definido el resultado del partido
        if not self.terminado():
            raise ValueError('No está definido el resultado del partido')
        # definir quien gano
        if self.goles_local > self.goles_visitante:
            return constants.GANA_LOCAL
        elif self.goles_local < self.goles_visitante:
            return constants.GANA_VISITANTE
        return constants.EMPATE

    def __str__(self):
        if self.terminado():
            return (f'{self.local.name} {self.goles_local} - '
                    f'{self.goles_visitante} {self.visitante.name}')
        return f'{self.local.name} - {self.visitante.name}'

    class Meta:
        ordering = ('fecha',)


class Apuesta(models.Model):
    """Define una apuesta realizada por un usuario.

    Como se apuesta?
    ================================

    Se puede apostar por dos cosas simultaneamente:
      * ganador: Apuesta quien gana el partido o empate (suma 1 punto)
      * goles: Apuesta la cantidad exacta de goles en el partido para cada
               equipo(suma 3 puntos).

    Un usuario puede apostar por cualquiera de los dos y no necesariamente
    tienen que coincidir estas apuestas. Por ejemplo uno puede apostar por
    ganador local y en resultado puede apostar por 0-0. Entonces, si el partido
    lo gana el local, el usuario lleva un punto, pero si empatan se lleva 3
    puntos

    Si el usuario acierta en el ganador y en el resultado, se lleva 4 puntos,
    es decir se suma el punto por ganador y los 3 puntos por resultado.
    """
    CHOICE_RESULTADO = (
        (constants.EMPATE, 'Empate'),
        (constants.GANA_LOCAL, 'Gana local'),
        (constants.GANA_VISITANTE, 'Gana visitante'),
    )
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL,
                                related_name='apuestas',
                                on_delete=models.CASCADE)
    partido = models.ForeignKey(Partido,
                                related_name='apuestas',
                                on_delete=models.CASCADE)
    ganador = models.CharField(max_length=1,
                               choices=CHOICE_RESULTADO,
                               default=constants.EMPATE)
    goles_local = models.PositiveSmallIntegerField(default=0)
    goles_visitante = models.PositiveSmallIntegerField(default=0)
    objects = managers.ApuestaManager()

    class Meta:
        # me aseguro que solo exista una apuesta por partido por usuario
        unique_together = ('usuario', 'partido')
        ordering = ('usuario__username',)

    def get_ganador_display(self):
        """Obtiene el ganador de forma bonita para mostrar"""
        if self.ganador == constants.GANA_LOCAL:
            return self.partido.local.name
        if self.ganador == constants.GANA_VISITANTE:
            return self.partido.visitante.name
        return 'Empate'

    @property
    def puntaje(self):
        """Devuelve los puntos obtenidos por la apuesta.

        Como se puntua?
        ===================================
            * 1 punto si acierta el ganador
            * 3 puntos si acierta la cantidad de goles por equipo
            * 4 puntos si acierta ambos
        """
        puntos = 0
        goles_local = self.partido.goles_local
        goles_visitante = self.partido.goles_visitante
        resultado = self.partido.resultado
        # verifico si coincide ganador
        if self.ganador == resultado:
            puntos += constants.PUNTOS_GANADOR
        # verifico si coincide goles
        if (self.goles_local == goles_local and
                self.goles_visitante == goles_visitante):
            puntos += constants.PUNTOS_GOLES
        return puntos

    def __str__(self):
        return f'Apuesta "{self.partido}" por {self.usuario}'
