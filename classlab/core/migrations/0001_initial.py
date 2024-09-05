from django.db import migrations
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType

# The same PERMISSIONS dictionary from the management command
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

def create_permissions(apps, schema_editor):
    # Get the Permission and Group models from the historical models
    Permission = apps.get_model('auth', 'Permission')
    Group = apps.get_model('auth', 'Group')
    ContentType = apps.get_model('contenttypes', 'ContentType')

    def _create_missing_permission(codename):
        content_type = ContentType.objects.get_for_model(Group)  # Adjust if needed
        permission, created = Permission.objects.get_or_create(
            codename=codename,
            name=f"Auto-generated permission: {codename}",
            content_type=content_type,
        )
        return permission

    # Ensure all necessary permissions exist
    for group_name, permissions in PERMISSIONS.items():
        group, _ = Group.objects.get_or_create(name=group_name)
        for permission_codename in permissions:
            permission = Permission.objects.filter(codename=permission_codename).first()
            if not permission:
                permission = _create_missing_permission(permission_codename)
            group.permissions.add(permission)

def delete_permissions(apps, schema_editor):
    # If you want to reverse the migration, you can remove these permissions/groups
    Permission = apps.get_model('auth', 'Permission')
    Group = apps.get_model('auth', 'Group')

    for group_name, permissions in PERMISSIONS.items():
        try:
            group = Group.objects.get(name=group_name)
            for permission_codename in permissions:
                permission = Permission.objects.filter(codename=permission_codename).first()
                if permission:
                    group.permissions.remove(permission)
        except Group.DoesNotExist:
            pass

class Migration(migrations.Migration):

    dependencies = [
        ('apps', '0001_initial'),
        ('administrators', '0002_alter_administrator_options'),
        ('classes', '0001_initial'),
        ('teachers', '0002_alter_teacher_options'),
        ('students', '0002_alter_student_options'),
        ('organisations', '0001_initial'),
        ('users', '0002_alter_user_user_type'),
    ]

    operations = [
        migrations.RunPython(create_permissions, delete_permissions),
    ]
