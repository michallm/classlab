from django.core.management.base import BaseCommand

from classlab.cloud.managers import K8sManager


class Command(BaseCommand):
    help = "Test connection to cluster."

    def handle(self, *args, **options):
        self.stdout.write("Testing connection to cluster...")
        k8s_manager = K8sManager()
        try:
            k8s_manager.test_connection()
        except Exception as e:  # noqa: BLE001
            self.stdout.write(self.style.ERROR(f"Failed to connect to cluster: {e}"))
            return

        self.stdout.write(self.style.SUCCESS("Successfully connected to cluster."))
