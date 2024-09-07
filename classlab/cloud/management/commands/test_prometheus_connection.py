from django.core.management.base import BaseCommand

from classlab.cloud.metrics import CloudMetrics


class Command(BaseCommand):
    help = "Test connection to prometheus."

    def handle(self, *args, **options):
        self.stdout.write("Testing connection to prometheus...")
        metrics = CloudMetrics("default")
        try:
            metrics.test_connection()
        except Exception as e:  # noqa: BLE001
            self.stdout.write(self.style.ERROR(f"Failed to connect to prometheus: {e}"))
            return

        self.stdout.write(self.style.SUCCESS("Successfully connected to prometheus."))
