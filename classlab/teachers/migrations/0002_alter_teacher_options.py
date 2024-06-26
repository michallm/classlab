# Generated by Django 4.1.8 on 2023-05-03 10:45

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("teachers", "0001_initial"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="teacher",
            options={
                "permissions": [
                    (
                        "teacher_resend_confirm_email",
                        "Can resend confirmation email to teacher",
                    )
                ],
                "verbose_name": "Teacher",
                "verbose_name_plural": "Teachers",
            },
        ),
    ]
