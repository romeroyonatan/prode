import factory
import factory.fuzzy

from django.utils import timezone

from prode.apuestas import constants
from prode.users.tests import factories as user_factories


class EtapaFactory(factory.django.DjangoModelFactory):
    nombre = factory.Sequence(lambda n: f"etapa-{n}")
    vencimiento = factory.fuzzy.FuzzyDateTime(timezone.now())
    slug = factory.Sequence(lambda n: f"etapa-{n}")
    publica = True

    class Meta:
        model = "apuestas.Etapa"


class PartidoFactory(factory.django.DjangoModelFactory):
    etapa = factory.SubFactory(EtapaFactory)
    fecha = factory.fuzzy.FuzzyDateTime(timezone.now())
    local = factory.Faker('country_code')
    visitante = factory.Faker('country_code')
    goles_local = factory.Faker('random_digit_not_null')
    goles_visitante = factory.Faker('random_digit_not_null')

    class Meta:
        model = "apuestas.Partido"


class ApuestaFactory(factory.django.DjangoModelFactory):
    usuario = factory.SubFactory(user_factories.UserFactory)
    partido = factory.SubFactory(PartidoFactory)
    ganador = factory.fuzzy.FuzzyChoice((constants.EMPATE,
                                         constants.GANA_LOCAL,
                                         constants.GANA_VISITANTE))
    goles_local = factory.Faker('random_digit_not_null')
    goles_visitante = factory.Faker('random_digit_not_null')

    class Meta:
        model = "apuestas.Apuesta"
