from django.apps import AppConfig


class ApuestasConfig(AppConfig):
    name = "prode.apuestas"
    verbose_name = "Apuestas"

    def ready(self):
        """Override this to put in:
            Users system checks
            Users signal registration
        """
        try:
            import users.signals  # noqa F401
        except ImportError:
            pass
