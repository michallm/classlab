from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as _

from classlab.classes.models import Class
from classlab.organisations.models import Organisation
from classlab.utils import generate_random_id

User = get_user_model()


class Teacher(models.Model):
    """Teacher model."""

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="teacher",
        verbose_name=_("User"),
    )
    teacher_id = models.CharField(
        _("Teacher ID"),
        max_length=12,
        unique=True,
        default=generate_random_id,
        editable=False,
    )
    organisation = models.ForeignKey(
        Organisation,
        on_delete=models.CASCADE,
        related_name="teachers",
        verbose_name=_("Organisation"),
    )
    classes = models.ManyToManyField(
        Class,
        related_name="teachers",
        verbose_name=_("Classes"),
        blank=True,
    )
    created_by = models.ForeignKey(
        User,
        on_delete=models.DO_NOTHING,
        related_name="created_teachers",
        verbose_name=_("Created by"),
        null=True,
        blank=True,
    )
    created_at = models.DateTimeField(_("Created at"), auto_now_add=True)
    updated_at = models.DateTimeField(_("Updated at"), auto_now=True)

    class Meta:
        verbose_name = _("Teacher")
        verbose_name_plural = _("Teachers")

        permissions = [
            (
                "teacher_resend_confirm_email",
                _("Can resend confirmation email to teacher"),
            ),
        ]

    def __str__(self):
        return self.user.get_full_name()

    def save(self, *args, **kwargs):
        if not self.pk:
            teacher_group = Group.objects.get(name="Teachers")
            self.user.groups.add(teacher_group)
        return super().save(*args, **kwargs)

    def clean(self):
        if self.user.organisation != self.organisation:
            raise ValidationError(
                {
                    "organisation": _(
                        "Teacher's organisation must be the same as the user's organisation.",  # noqa: E501
                    ),
                },
            )

        if (
            self.organisation.quota.max_number_of_teachers
            <= self.organisation.teachers.count()
        ):
            raise ValidationError(
                {
                    "organisation": _(
                        "Teacher's organisation has reached the maximum number of teachers.",  # noqa: E501
                    ),
                },
            )
