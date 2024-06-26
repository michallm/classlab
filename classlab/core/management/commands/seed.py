from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

User = get_user_model()


class Command(BaseCommand):
    help = "Seed the database with test data."

    def handle(self, *args, **options):
        self.stdout.write("Seeding database...")
