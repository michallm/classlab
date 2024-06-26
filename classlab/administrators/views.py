import logging

from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.http import JsonResponse
from django.shortcuts import redirect
from django.utils.translation import gettext_lazy as _
from django.views.generic import TemplateView
from django.views.generic import View

from classlab.cloud.metrics import CloudMetrics

logger = logging.getLogger(__name__)


class AdministratorHomeView(LoginRequiredMixin, View):
    def get(self, request):
        return redirect("classes:list")


class AdministratorDashboardView(
    LoginRequiredMixin,
    PermissionRequiredMixin,
    TemplateView,
):
    template_name = "administrators/dashboard.html"
    permission_required = "administrators.view_dashboard"


class BaseResourceView(LoginRequiredMixin, PermissionRequiredMixin, View):
    metric_name: str
    metric_unit: str | None = None
    permission_required = "administrators.view_dashboard"

    def get(self, request):
        try:
            metrics = CloudMetrics(
                self.request.user.organisation.cluster_config.namespace,
            )
            usage = metrics.get_resource("used", self.metric_name, self.metric_unit)
            limit = metrics.get_resource("hard", self.metric_name, self.metric_unit)
        except Exception:
            logger.exception("Error retrieving resources")
            return JsonResponse({"error": _("Error retrieving resources")}, status=500)

        return JsonResponse(
            {
                "usage": usage,
                "limit": limit,
            },
        )


class CPUResourceView(BaseResourceView):
    metric_name = "limits.cpu"


class MemoryResourceView(BaseResourceView):
    metric_name = "limits.memory"
    metric_unit = "Mi"


class StorageResourceView(BaseResourceView):
    metric_name = "requests.storage"
    metric_unit = "Gi"
