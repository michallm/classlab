from django.db import models
from django.utils.translation import gettext_lazy as _

from classlab.organisations.models import Organisation

from .tasks import create_namespace
from .tasks import set_resource_quota


class ClusterConfig(models.Model):
    name = models.CharField(_("Name"), max_length=255)
    organisation = models.OneToOneField(
        Organisation,
        on_delete=models.CASCADE,
        related_name="cluster_config",
        verbose_name=_("Organisation"),
    )
    namespace = models.CharField(_("Namespace"), max_length=255)
    spot_pool = models.BooleanField(_("Spot Pool"), default=True)

    class Meta:
        verbose_name = _("Cluster Config")
        verbose_name_plural = _("Cluster Configs")

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.pk:
            create_namespace.delay(self.namespace)
        super().save(*args, **kwargs)


class ResourceQuota(models.Model):
    """
    Represents limits applies to organisation namespace
    """

    orgnisation = models.OneToOneField(
        Organisation,
        on_delete=models.CASCADE,
        related_name="resource_quota",
        verbose_name=_("Organisation"),
    )
    cpu = models.IntegerField(_("CPU"), help_text=_("CPU in millicores"))
    memory = models.IntegerField(_("Memory"), help_text=_("Memory in MiB"))
    storage = models.IntegerField(_("Storage"), help_text=_("Storage in GiB"))

    class Meta:
        verbose_name = _("Resource Quota")
        verbose_name_plural = _("Resource Quotas")

    def __str__(self):
        return f"{self.orgnisation.name} - Resource Quota"

    def save(self, *args, **kwargs):
        set_resource_quota.delay(
            self.namespace,
            {
                "cpu": self.cpu,
                "memory": self.memory,
                "storage": self.storage,
            },
        )
        super().save(*args, **kwargs)

    @property
    def namespace(self):
        return self.orgnisation.cluster_config.namespace
