from django.apps import AppConfig
from django.core import checks


class CoreConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "classlab.core"

    def ready(self):
        from classlab.core.checks import check_dev_mode

        checks.register(check_dev_mode)
