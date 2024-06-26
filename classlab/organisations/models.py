from django.contrib.auth import get_user_model
from django.db import models
from django.utils.translation import gettext_lazy as _

from classlab.utils import generate_random_id

User = get_user_model()


class Organisation(models.Model):
    """Organisation model."""

    organisation_id = models.CharField(
        _("Organisation ID"),
        max_length=12,
        unique=True,
        default=generate_random_id,
        editable=False,
    )
    name = models.CharField(_("Name"), max_length=255)
    slug = models.SlugField(_("Slug"), max_length=255, unique=True)
    created_by = models.ForeignKey(
        User,
        on_delete=models.DO_NOTHING,
        related_name="created_organisations",
        verbose_name=_("Created by"),
        null=True,
        blank=True,
    )
    created_at = models.DateTimeField(_("Created at"), auto_now_add=True)
    updated_at = models.DateTimeField(_("Updated at"), auto_now=True)

    class Meta:
        verbose_name = _("Organisation")
        verbose_name_plural = _("Organisations")

    def __str__(self):
        return self.name

    @property
    def namespace(self):
        return self.cluster_config.namespace


class OrganisationQuota(models.Model):
    """Organisation quota model."""

    organisation = models.OneToOneField(
        Organisation,
        on_delete=models.CASCADE,
        related_name="quota",
        verbose_name=_("Organisation"),
    )
    max_number_of_students = models.PositiveIntegerField(
        _("Max number of students"),
        default=0,
    )
    max_number_of_teachers = models.PositiveIntegerField(
        _("Max number of teachers"),
        default=0,
    )
    max_number_of_apps_per_student = models.PositiveIntegerField(
        _("Max number of apps per student"),
        default=0,
    )
    max_number_of_apps_per_teacher = models.PositiveIntegerField(
        _("Max number of apps per teacher"),
        default=0,
    )

    class Meta:
        verbose_name = _("Organisation Quota")
        verbose_name_plural = _("Organisation Quotas")

    def __str__(self):
        return f"{self.organisation.name} Quota"
