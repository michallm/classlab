from functools import cache

from django.conf import settings
from django.utils import timezone
from prometheus_api_client import PrometheusConnect
from prometheus_api_client.utils import parse_datetime

# TODO: move to settings
RESOLUTION = "1h"


@cache
def convert_unit(raw_value: str, unit: str) -> float:
    value = float(raw_value)
    # kubernetes units conversion
    if unit == "Ki":
        return value / 1024
    elif unit == "Mi":  # noqa: RET505
        return value / 1024 / 1024
    elif unit == "Gi":
        return value / 1024 / 1024 / 1024

    return value


class CloudMetrics:
    def __init__(self, namespace: str):
        self.namespace = namespace
        self.prom = PrometheusConnect(
            url=settings.PROMETHEUS_URL,
            disable_ssl=settings.PROMETHEUS_DISABLE_SSL,
        )

    def get_resource(
        self,
        resource_type: str,
        resource: str,
        unit: str | None = None,
    ) -> list:
        # available resources - limits.cpu, limits.memory, requests.storage
        start_time = parse_datetime("30d")
        end_time = parse_datetime("now")
        step = RESOLUTION

        metric_data = self.prom.custom_query_range(
            query=(
                "max by (resource)"
                f"(max_over_time(kube_resourcequota{{namespace='{self.namespace}',"
                f" type='{resource_type}', resource='{resource}'}}[{step}]))"
            ),
            start_time=start_time,
            end_time=end_time,
            step=step,
        )
        return [
            [
                timezone.datetime.fromtimestamp(value[0]),
                convert_unit(value[1], unit),
            ]
            for metric in metric_data
            for value in metric["values"]
        ]
