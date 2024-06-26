from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.db import models
from django.utils.translation import gettext_lazy as _

from classlab.organisations.models import Organisation
from classlab.utils import generate_random_id

User = get_user_model()


class Administrator(models.Model):
    """Administrator model."""

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="administrator",
        verbose_name=_("User"),
    )
    administrator_id = models.CharField(
        _("Administrator ID"),
        max_length=12,
        unique=True,
        default=generate_random_id,
        editable=False,
    )
    organisation = models.ForeignKey(
        Organisation,
        on_delete=models.CASCADE,
        related_name="administrators",
        verbose_name=_("Organisation"),
    )
    created_by = models.ForeignKey(
        User,
        on_delete=models.DO_NOTHING,
        related_name="created_administrators",
        verbose_name=_("Created by"),
        null=True,
        blank=True,
    )
    created_at = models.DateTimeField(_("Created at"), auto_now_add=True)
    updated_at = models.DateTimeField(_("Updated at"), auto_now=True)

    class Meta:
        verbose_name = _("Administrator")
        verbose_name_plural = _("Administrators")
        permissions = [
            ("view_dashboard", _("Can view dashboard")),
        ]

    def __str__(self):
        return self.user.get_full_name()

    def save(self, *args, **kwargs):
        if not self.pk:
            group = Group.objects.get(name="Administrators")
            self.user.groups.add(group)

        return super().save(*args, **kwargs)
