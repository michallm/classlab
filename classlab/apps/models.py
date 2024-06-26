import base64
import logging

import reversion
import yaml
from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import models
from django.template import Context
from django.template import Template
from django.urls import reverse
from django.utils import timezone
from django.utils.functional import cached_property
from django.utils.translation import gettext_lazy as _

from classlab.classes.models import Class
from classlab.cloud import exceptions
from classlab.cloud.managers import AppStatus
from classlab.cloud.managers import K8sManager
from classlab.cloud.tasks import create_app
from classlab.cloud.tasks import delete_app
from classlab.cloud.tasks import start_app
from classlab.cloud.tasks import stop_app
from classlab.organisations.models import Organisation
from classlab.utils import generate_random_id
from classlab.utils.generator import generate_random_password
from classlab.utils.generator import generate_username
from classlab.utils.run_command_generator import RunCommandGenerator

User = get_user_model()

logger = logging.getLogger(__name__)


class AppCategory(models.Model):
    """A category for apps"""

    name = models.CharField(_("Name"), max_length=100)
    slug = models.SlugField(_("Slug"), max_length=100, unique=True)
    created_at = models.DateTimeField(_("Created at"), auto_now_add=True)
    updated_at = models.DateTimeField(_("Updated at"), auto_now=True)

    class Meta:
        verbose_name = _("App Category")
        verbose_name_plural = _("App Categories")

    def __str__(self):
        return self.name


@reversion.register()
class AppTemplate(models.Model):
    """An app template is a collection of modules that can be used by a user"""

    template_id = models.CharField(
        _("Template ID"),
        max_length=12,
        default=generate_random_id,
        unique=True,
        editable=False,
    )
    name = models.CharField(_("Name"), max_length=100)
    category = models.ForeignKey(
        AppCategory,
        on_delete=models.CASCADE,
        related_name="app_templates",
        verbose_name=_("Category"),
    )
    expose_node_port = models.BooleanField(_("Expose Node Port"), default=False)
    run_command_template = models.TextField(  # noqa: DJ001
        _("Run Command Template"),
        blank=True,
        null=True,
        help_text=_("A template for the command that will help user to run the app. "),
    )
    organisations = models.ManyToManyField(
        Organisation,
        related_name="app_templates",
        related_query_name="app_template",
        verbose_name=_("Organisations"),
    )
    managed = models.BooleanField(_("Managed"), default=False)
    manifest = models.TextField(_("Manifest"))
    description = models.TextField(_("Description"), blank=True)
    created_at = models.DateTimeField(_("Created at"), auto_now_add=True)
    updated_at = models.DateTimeField(_("Updated at"), auto_now=True)

    class Meta:
        verbose_name = _("App Template")
        verbose_name_plural = _("App Templates")
        unique_together = ("name", "template_id")

    def __str__(self):
        if self.managed:
            return f"{self.name} ({_('Managed')})"

        return self.name


class AppTemplateKeyValue(models.Model):
    """A key-value pair for an app template"""

    class Type(models.TextChoices):
        STRING = "string", _("String")
        NUMBER = "number", _("Number")
        BOOLEAN = "boolean", _("Boolean")

    class Generator(models.TextChoices):
        PASSWORD = "password", _("Password")
        USERNAME = "username", _("Username")

    app_template = models.ForeignKey(
        AppTemplate,
        on_delete=models.CASCADE,
        related_name="key_values",
        verbose_name=_("App Template"),
    )
    teacher_only = models.BooleanField(_("Teacher Only"), default=False)
    student_only = models.BooleanField(_("Student Only"), default=False)
    name = models.CharField(_("Name"), max_length=100)
    description = models.TextField(_("Description"), blank=True)
    key = models.CharField(_("Key"), max_length=100)
    type = models.CharField(
        _("Type"),
        max_length=10,
        choices=Type.choices,
        default=Type.STRING,
    )
    required = models.BooleanField(_("Required"), default=False)
    editable = models.BooleanField(_("Editable"), default=True)
    secret = models.BooleanField(_("Secret"), default=False)
    generated = models.BooleanField(_("Generated"), default=False)
    generator = models.CharField(  # noqa: DJ001
        _("Generator"),
        max_length=10,
        choices=Generator.choices,
        blank=True,
        null=True,
    )
    end_user_editable = models.BooleanField(_("End User Editable"), default=False)
    created_at = models.DateTimeField(_("Created at"), auto_now_add=True)
    updated_at = models.DateTimeField(_("Updated at"), auto_now=True)

    class Meta:
        unique_together = ("app_template", "key")
        verbose_name = _("App Template Key Value")
        verbose_name_plural = _("App Template Key Values")

    def __str__(self):
        return f"{self.app_template.name} - {self.name}"

    @property
    def is_managed(self):
        return self.app_template.managed

    def generate(self, value: str | None = None) -> str:
        """Generate the value of the key"""
        if self.generator == self.Generator.PASSWORD:
            return generate_random_password()

        elif self.generator == self.Generator.USERNAME:  # noqa: RET505
            return generate_username(value)

        return value


class App(models.Model):
    app_id = models.CharField(
        _("App ID"),
        max_length=12,
        default=generate_random_id,
        unique=True,
        editable=False,
    )
    name = models.CharField(_("Name"), max_length=100)
    managed_app = models.ForeignKey(
        "ManagedApp",
        on_delete=models.CASCADE,
        related_name="apps",
        null=True,
        blank=True,
        verbose_name=_("Managed App"),
    )
    template = models.ForeignKey(
        AppTemplate,
        on_delete=models.CASCADE,
        related_name="apps",
        verbose_name=_("Template"),
    )
    organisation = models.ForeignKey(
        Organisation,
        on_delete=models.CASCADE,
        related_name="apps",
        related_query_name="app",
        verbose_name=_("Organisation"),
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="apps",
        related_query_name="app",
        verbose_name=_("User"),
    )
    created_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="created_apps",
        null=True,
        blank=True,
        verbose_name=_("Created by"),
    )
    created_at = models.DateTimeField(_("Created at"), auto_now_add=True)
    updated_at = models.DateTimeField(_("Updated at"), auto_now=True)

    class Meta:
        verbose_name = _("App")
        verbose_name_plural = _("Apps")
        unique_together = ("user", "name")

        permissions = [
            (
                "start_app",
                _("Can start an app"),
            ),
            (
                "stop_app",
                _("Can stop an app"),
            ),
        ]

    def __str__(self):
        return self.app_id

    def save(self, *args, **kwargs):
        if not self.pk:
            self.created_by = self.user

        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("apps:detail", kwargs={"app_id": self.app_id})

    @property
    def namespace(self):
        return self.organisation.namespace

    def get_basic_config(self) -> dict:
        """Return the basic config for the app"""
        return {
            "namespace": self.namespace,
            "app_id": self.app_id,
            "name": self.name,
            "user_id": self.user.user_id,
            "spot_pool": self.organisation.cluster_config.spot_pool,
            "proxy_domain": settings.PROXY_DOMAIN,
        }

    @property
    def manifest(self):
        """Return the manifest for the app"""
        return self.template.manifest

    def generate_manifest(self, config: dict | None = None) -> dict:
        """Generate the manifest for the app

        Use Django templating to load the template manifest and apply values
        from the config.
        The template should inlcude a filter for b64encode to encode strings as base64.
        """
        cfg = self.get_basic_config()
        if config:
            cfg.update(config)

        ctx = Context(cfg)
        template = Template(self.manifest)
        rendered = template.render(ctx)
        return list(yaml.safe_load_all(rendered))

    def get_key_vaules(self) -> dict:
        """Return the config for the app

        Does not include secret values
        """
        return {kv.key: kv.value for kv in self.key_values.filter(secret=False)}

    @cached_property
    def status(self) -> AppStatus:
        """Return the status of the app"""

        k8s = K8sManager()
        try:
            return k8s.get_app_status(
                namespace=self.namespace,
                manifest=self.generate_manifest(),
            )

        except exceptions.CloudResourceNotFoundError:
            logger.exception("Failed to get app status - resource not found")
            return AppStatus.ERROR

        except Exception:
            logger.exception("Failed to get app status")
            return AppStatus.ERROR

    @property
    def run_command(self):
        """Return the run command for the app"""
        if not self.template.run_command_template:
            return None
        data = self.get_run_command_data()
        generator = RunCommandGenerator(self.template.run_command_template, data)
        return generator.generate()

    @cached_property
    def verbose_status(self) -> str:  # noqa: PLR0911
        if not self.status:
            return _("Unknown")

        time_threshold = 15
        if (timezone.now() - self.created_at).total_seconds() < time_threshold:
            return _("Creating")

        status = AppStatus(self.status)
        if status == AppStatus.RUNNING:
            return _("Running")
        elif status == AppStatus.STOPPED:  # noqa: RET505
            return _("Stopped")
        elif status == AppStatus.STARTING:
            return _("Starting")
        elif status == AppStatus.STOPPING:
            return _("Stopping")
        elif status == AppStatus.CREATING:
            return _("Creating")
        elif status == AppStatus.DELETING:
            return _("Deleting")
        elif status == AppStatus.ERROR:
            return _("Error")

        return _("Unknown")

    def get_status(self) -> dict:
        """Return the status of the app"""
        time_threshold = 15
        if (timezone.now() - self.created_at).total_seconds() < time_threshold:
            status = AppStatus.CREATING
            verbose_status = _("Creating")
        else:
            status = self.status
            verbose_status = status.verbose_name

        return {
            "status": status.value,
            "verbose_status": verbose_status,
        }

    def start(self):
        """Start the app"""
        logger.debug("Starting app %s", self.app_id)
        start_app.delay(self.namespace, self.app_id)

    def stop(self):
        """Stop the app"""
        logger.debug("Stopping app %s", self.app_id)
        stop_app.delay(self.namespace, self.app_id)

    @property
    def category(self):
        """Return the category of the app"""
        return self.template.category

    def get_run_command_data(self):
        """Return the run command data of the app"""
        try:
            k8s = K8sManager()
            data = {
                "host": f"{self.app_id}.{settings.PROXY_DOMAIN}",
            }
            if self.template.expose_node_port:
                node_port = k8s.get_app_node_port(
                    namespace=self.namespace,
                    manifest=self.generate_manifest(),
                )
                data["port"] = node_port

        except Exception:
            logger.exception("Failed to get run command data")
            return {}

        else:
            return data

    @property
    def url(self):
        """Return the url of the app"""
        if self.template.expose_node_port:
            k8s = K8sManager()
            try:
                node_port = k8s.get_app_node_port(
                    namespace=self.namespace,
                    manifest=self.generate_manifest(),
                )

            except Exception:
                logger.exception("Failed to get node port")
                msg = "Unable to get node port"
                raise Exception(msg) from None  # noqa: TRY002

            else:
                return f"{self.app_id}.{settings.PROXY_DOMAIN}:{node_port}"

        return f"https://{self.app_id}.{settings.PROXY_DOMAIN}"

    def create(self, config: dict):
        """Create the app"""
        logger.debug("Creating app %s", self.app_id)
        create_app.delay(self.app_id, config)

    def delete(self, *args, **kwargs):
        """Delete the app"""
        logger.debug("Deleting app %s", self.app_id)
        delete_app.delay(self.namespace, self.generate_manifest())
        super().delete(*args, **kwargs)

    @property
    def contain_generated_values(self):
        """Return whether the app contains generated values"""
        return AppTemplateKeyValue.objects.filter(
            app_template=self.template,
            generated=True,
            student_only=False,
            teacher_only=False,
        ).exists()

    def get_generated_values(self, *, teacher_only=False, student_only=False):
        """Return the generated values for the app"""
        try:
            if teacher_only:
                values = AppTemplateKeyValue.objects.filter(
                    app_template=self.template,
                    generated=True,
                    teacher_only=True,
                )
            elif student_only:
                values = AppTemplateKeyValue.objects.filter(
                    app_template=self.template,
                    generated=True,
                    student_only=True,
                )
            else:
                values = AppTemplateKeyValue.objects.filter(
                    app_template=self.template,
                    generated=True,
                    student_only=False,
                    teacher_only=False,
                )

            k8s = K8sManager()

            secrets = k8s.get_secret(
                namespace=self.namespace,
                secret_name=self.app_id,
            )

            to_return = {}
            for value in values:
                if value.key in secrets["data"]:
                    raw_value = secrets["data"][value.key]
                    decoded_value = base64.b64decode(raw_value).decode("utf-8")
                    to_return[value.name] = {
                        "key": value.key,
                        "value": decoded_value,
                        "secret": value.secret,
                    }
        except Exception:
            logger.exception("Failed to get generated values")
            return {}
        else:
            return to_return

    @property
    def details(self) -> bool:
        """Return the details of the app"""
        conditions = [self.contain_generated_values]
        return any(conditions)

    @property
    def contain_teacher_only_generated_values(self):
        """Return whether the app contains generated values"""
        return AppTemplateKeyValue.objects.filter(
            app_template=self.template,
            generated=True,
            teacher_only=True,
            student_only=False,
        ).exists()

    @property
    def contain_student_only_generated_values(self):
        """Return whether the app contains generated values"""
        return AppTemplateKeyValue.objects.filter(
            app_template=self.template,
            generated=True,
            student_only=True,
            teacher_only=False,
        ).exists()

    def get_generated_teacher_values(self):
        """Return the generated values for the app"""
        return self.get_generated_values(teacher_only=True)

    def get_generated_student_values(self):
        """Return the generated values for the app"""
        return self.get_generated_values(student_only=True)


class ManagedApp(models.Model):
    """
    It represents group of apps that are managed by the organisation
    and are assigned to a class.
    """

    managed_app_id = models.CharField(
        _("Managed App ID"),
        max_length=12,
        default=generate_random_id,
        unique=True,
        editable=False,
    )

    name = models.CharField(_("Name"), max_length=100)
    template = models.ForeignKey(
        AppTemplate,
        on_delete=models.CASCADE,
        related_name="managed_apps",
        verbose_name=_("Template"),
    )
    organisation = models.ForeignKey(
        Organisation,
        on_delete=models.CASCADE,
        related_name="managed_apps",
        related_query_name="managed_app",
        verbose_name=_("Organisation"),
    )
    assigned_class = models.ForeignKey(
        Class,
        on_delete=models.CASCADE,
        related_name="managed_apps",
        related_query_name="managed_app",
        verbose_name=_("Class"),
    )
    created_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="created_managed_apps",
        null=True,
        blank=True,
        verbose_name=_("Created by"),
    )
    created_at = models.DateTimeField(_("Created at"), auto_now_add=True)
    updated_at = models.DateTimeField(_("Updated at"), auto_now=True)

    class Meta:
        verbose_name = _("Managed App")
        verbose_name_plural = _("Managed Apps")
        unique_together = ("assigned_class", "name")

    def __str__(self):
        return self.managed_app_id
