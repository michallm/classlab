# Generated by Django 4.0.10 on 2023-04-26 17:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('apps', '0002_alter_app_options'),
    ]

    operations = [
        migrations.AddField(
            model_name='apptemplate',
            name='expose_node_port',
            field=models.BooleanField(default=False, verbose_name='Expose Node Port'),
        ),
        migrations.AddField(
            model_name='apptemplate',
            name='run_command_template',
            field=models.TextField(blank=True, help_text='A template for the command that will help user to run the app. ', null=True, verbose_name='Run Command Template'),
        ),
    ]
