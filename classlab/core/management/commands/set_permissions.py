from django.contrib.auth.models import Group
from django.contrib.auth.models import Permission
from django.core.exceptions import ValidationError
from django.core.management.base import BaseCommand
from django.utils.translation import gettext_lazy as _

PERMISSIONS = {
    "Administrators": [
        "view_organisation",
        "add_teacher",
        "change_teacher",
        "delete_teacher",
        "view_teacher",
        "teacher_resend_confirm_email",
        "student_resend_confirm_email",
        "add_student",
        "change_student",
        "delete_student",
        "view_student",
        "add_class",
        "change_class",
        "delete_class",
        "view_class",
        "view_dashboard",
    ],
    "Teachers": [
        "view_teacher",
        "add_student",
        "change_student",
        "delete_student",
        "view_student",
        "student_resend_confirm_email",
        "add_app",
        "change_app",
        "delete_app",
        "view_app",
        "start_app",
        "stop_app",
        "view_class",
        "add_managedapp",
        "view_managedapp",
        "change_managedapp",
        "delete_managedapp",
    ],
    "Students": [
        "view_student",
        "add_app",
        "change_app",
        "delete_app",
        "view_app",
        "start_app",
        "stop_app",
    ],
}


class Command(BaseCommand):
    help = "Set permissions for groups"

    def _check_if_permissions_exist(self):
        permissions = set()
        for group_permissions in PERMISSIONS.values():
            for permission in group_permissions:
                permissions.add(permission)

        for permission in permissions:
            try:
                Permission.objects.get(codename=permission)
            except Permission.DoesNotExist:
                raise ValidationError(
                    _(
                        "Permission %s does not exist. Please create it before running this command.",  # noqa: E501
                    )
                    % permission,
                ) from None

    def handle(self, *args, **options):
        """
        Set permissions for groups
        """

        # check if permissions exist
        self._check_if_permissions_exist()

        for group_name, permissions in PERMISSIONS.items():
            group, created = Group.objects.get_or_create(name=group_name)
            for permission in permissions:
                perm = Permission.objects.get(codename=permission)
                group.permissions.add(perm)
            self.stdout.write(self.style.SUCCESS(f"Added permissions to {group_name}"))
