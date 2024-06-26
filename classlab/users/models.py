from allauth.account.utils import send_email_confirmation
from django.contrib.auth.models import AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin
from django.db import models
from django.urls import reverse
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from classlab.utils import generate_random_id

from .managers import UserManager


class User(AbstractBaseUser, PermissionsMixin):
    """Custom user model."""

    class UserType(models.TextChoices):
        STUDENT = "STUDENT", _("Student")
        TEACHER = "TEACHER", _("Teacher")
        ADMIN = "ADMIN", _("Organization Administrator")

    user_id = models.CharField(
        _("user id"),
        max_length=12,
        default=generate_random_id,
        unique=True,
        editable=False,
    )
    user_type = models.CharField(  # noqa: DJ001
        _("user type"),
        max_length=7,
        choices=UserType.choices,
        blank=True,
        null=True,
    )
    email = models.EmailField(_("email address"), unique=True)
    first_name = models.CharField(_("first name"), max_length=30, blank=True)
    last_name = models.CharField(_("last name"), max_length=150, blank=True)
    is_staff = models.BooleanField(
        _("staff status"),
        default=False,
        help_text=_("Designates whether the user can log into this admin site."),
    )
    is_active = models.BooleanField(
        _("active"),
        default=True,
        help_text=_(
            "Designates whether this user should be treated as active. Unselect this instead of deleting accounts.",  # noqa: E501
        ),
    )
    date_joined = models.DateTimeField(_("date joined"), default=timezone.now)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["first_name", "last_name"]

    objects = UserManager()

    class Meta:
        verbose_name = _("user")
        verbose_name_plural = _("users")
        ordering = ["email"]

    def __str__(self):
        """Return email."""
        return self.email

    def get_full_name(self):
        """Return full name of user."""
        return f"{self.first_name} {self.last_name}"

    def get_short_name(self):
        """Return short name of user."""
        return self.first_name

    def get_absolute_url(self):
        """Get url for user's detail view.

        Returns:
            str: URL for user detail.

        """
        return reverse("users:detail", kwargs={"user_id": self.user_id})

    @property
    def is_administrator(self):
        """Check if user is an administrator.

        Returns:
            bool: True if user is an administrator, False otherwise.

        """
        return self.user_type == self.UserType.ADMIN

    @property
    def is_teacher(self):
        """Check if user is a teacher.

        Returns:
            bool: True if user is a teacher, False otherwise.

        """
        return self.user_type == self.UserType.TEACHER

    @property
    def is_student(self):
        """Check if user is a student.

        Returns:
            bool: True if user is a student, False otherwise.

        """
        return self.user_type == self.UserType.STUDENT

    @property
    def organisation(self):
        """Get organisation of user.

        Returns:
            Organisation: Organisation of user.

        """
        if self.is_administrator:
            return self.administrator.organisation

        if self.is_teacher:
            return self.teacher.organisation

        if self.is_student:
            return self.student.organisation

        return None

    def send_confirmation_email(self, request):
        """Send confirmation email to user."""
        send_email_confirmation(request, self)
