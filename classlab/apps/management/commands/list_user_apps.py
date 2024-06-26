from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.core.management.base import CommandError

from classlab.apps.models import App

User = get_user_model()


class Command(BaseCommand):
    help = "Lists all apps for a user"

    def add_arguments(self, parser):
        parser.add_argument("user", type=str, help="Email of the user to list apps for")
        parser.add_argument(
            "--only-id",
            action="store_true",
            help="Only print the app IDs",
        )

    def handle(self, *args, **options):
        user = options["user"]

        try:
            user = User.objects.get(email=user)
        except User.DoesNotExist:
            msg = "User does not exist"
            raise CommandError(msg) from None

        apps = App.objects.filter(user=user)

        for app in apps:
            if options["only_id"]:
                self.stdout.write(self.style.SUCCESS(f"{app.app_id}"))
                continue

            self.stdout.write(self.style.SUCCESS(f"App: {app.name}"))
