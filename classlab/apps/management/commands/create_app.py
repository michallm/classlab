import time

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.core.management.base import CommandError

from classlab.apps.models import App
from classlab.apps.models import AppTemplate

User = get_user_model()


class Command(BaseCommand):
    help = "Creates a new app"

    def add_arguments(self, parser):
        parser.add_argument("template_id", type=str, help="ID of the template to use")
        parser.add_argument("prefix", type=str, help="Prefix for the app name")
        parser.add_argument(
            "user",
            type=str,
            help="Email of the user to create the app for",
        )
        parser.add_argument(
            "--count",
            type=int,
            help="Number of apps to create",
            default=1,
        )
        parser.add_argument(
            "--wait",
            type=int,
            help="Wait time between app creation",
            default=0,
        )
        parser.add_argument(
            "--delete-after",
            type=int,
            help="Delete app after N minutes",
            default=-1,
        )

    def handle(self, *args, **options):
        template_id = options["template_id"]
        prefix = options["prefix"]
        user = options["user"]
        count = options["count"]

        try:
            template = AppTemplate.objects.get(template_id=template_id)
        except AppTemplate.DoesNotExist:
            msg = "Template does not exist"
            raise CommandError(msg) from None

        try:
            user = User.objects.get(email=user)
        except User.DoesNotExist:
            msg = "User does not exist"
            raise CommandError(msg) from None

        if options["delete_after"] > 0:
            to_delete = []

        for i in range(count):
            app = App.objects.create(
                user=user,
                template=template,
                name=f"{prefix}-{i+1}",
                organisation=user.organisation,
            )
            app.create({})
            if options["delete_after"] > 0:
                to_delete.append(app.app_id)
            self.stdout.write(self.style.SUCCESS(f"Created app {app.name}"))
            self.stdout.write(f"Wating {options['wait']} seconds...")
            time.sleep(options["wait"])

        if options["delete_after"] > 0:
            self.stdout.write(
                f"Waiting {options['delete_after']} minutes before deleting...",
            )
            time.sleep(options["delete_after"])

            for app_id in to_delete:
                try:
                    app = App.objects.delete(app_id=app_id)
                except App.DoesNotExist:
                    msg = "App does not exist"
                    raise CommandError(msg) from None

            self.stdout.write(self.style.SUCCESS(f"Deleted {len(to_delete)} apps"))
