from django.core.management.base import BaseCommand
from django.core.management.base import CommandError

from classlab.apps.models import App


class Command(BaseCommand):
    help = "Deletes an list of apps"

    def add_arguments(self, parser):
        parser.add_argument(
            "app_ids",
            nargs="+",
            type=str,
            help="IDs of the apps to delete",
        )

    def handle(self, *args, **options):
        app_ids = options["app_ids"]

        for app_id in app_ids:
            try:
                app = App.objects.get(app_id=app_id)
            except App.DoesNotExist:
                msg = f"App {app_id} does not exist"
                raise CommandError(msg) from None

            app.delete()
            self.stdout.write(self.style.SUCCESS(f"Deleted app {app.name}"))

        self.stdout.write(self.style.SUCCESS(f"Deleted {len(app_ids)} apps"))
