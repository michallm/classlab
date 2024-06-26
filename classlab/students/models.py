from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as _

from classlab.classes.models import Class
from classlab.organisations.models import Organisation
from classlab.utils import generate_random_id

User = get_user_model()


class Student(models.Model):
    """Student model."""

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="student",
        verbose_name=_("User"),
    )
    student_id = models.CharField(
        _("Student ID"),
        max_length=12,
        unique=True,
        default=generate_random_id,
        editable=False,
    )
    organisation = models.ForeignKey(
        Organisation,
        on_delete=models.CASCADE,
        related_name="students",
        verbose_name=_("Organisation"),
    )
    student_class = models.ForeignKey(
        Class,
        on_delete=models.CASCADE,
        related_name="students",
        verbose_name=_("Class"),
    )
    created_by = models.ForeignKey(
        User,
        on_delete=models.DO_NOTHING,
        related_name="created_students",
        verbose_name=_("Created by"),
        null=True,
        blank=True,
    )
    created_at = models.DateTimeField(_("Created at"), auto_now_add=True)
    updated_at = models.DateTimeField(_("Updated at"), auto_now=True)

    class Meta:
        verbose_name = _("Student")
        verbose_name_plural = _("Students")

        permissions = [
            (
                "student_resend_confirm_email",
                _("Can resend confirmation email to student"),
            ),
        ]

    def __str__(self):
        return self.user.get_full_name()

    def save(self, *args, **kwargs):
        if not self.pk:
            group = Group.objects.get(name="Students")
            self.user.groups.add(group)
        return super().save(*args, **kwargs)

    def clean(self):
        if self.organisation != self.student_class.organisation:
            raise ValidationError(
                {
                    "student_class": _(
                        "Class does not belong to the same organisation as the student.",  # noqa: E501
                    ),
                },
            )
        if (
            self.organisation.quota.max_number_of_students
            <= self.organisation.students.count()
        ):
            raise ValidationError(
                {
                    "organisation": _(
                        "Organisation has reached the maximum number of students.",
                    ),
                },
            )
