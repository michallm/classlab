from django.contrib.auth import get_user_model
from django.db import models
from django.utils.translation import gettext_lazy as _

from classlab.organisations.models import Organisation
from classlab.utils import generate_random_id

User = get_user_model()


class Class(models.Model):
    """Class model."""

    class_id = models.CharField(
        _("Class ID"),
        max_length=12,
        unique=True,
        default=generate_random_id,
        editable=False,
    )
    name = models.CharField(_("Name"), max_length=255)
    organisation = models.ForeignKey(
        Organisation,
        on_delete=models.CASCADE,
        related_name="classes",
        verbose_name=_("Organisation"),
    )
    created_by = models.ForeignKey(
        User,
        on_delete=models.DO_NOTHING,
        related_name="created_classes",
        verbose_name=_("Created by"),
        null=True,
        blank=True,
    )
    created_at = models.DateTimeField(_("Created at"), auto_now_add=True)
    updated_at = models.DateTimeField(_("Updated at"), auto_now=True)

    class Meta:
        verbose_name = _("Class")
        verbose_name_plural = _("Classes")
        ordering = ["name"]

    def __str__(self):
        return self.name
