from django.core.management.base import BaseCommand
from django.core.management.base import CommandError

from classlab.apps.models import App


class Command(BaseCommand):
    help = "Deletes an app"

    def add_arguments(self, parser):
        parser.add_argument("app_id", type=str, help="ID of the app to delete")

    def handle(self, *args, **options):
        app_id = options["app_id"]

        try:
            app = App.objects.get(app_id=app_id)
        except App.DoesNotExist:
            msg = "App does not exist"
            raise CommandError(msg) from None

        app.delete()
        self.stdout.write(self.style.SUCCESS(f"Deleted app {app.name}"))
