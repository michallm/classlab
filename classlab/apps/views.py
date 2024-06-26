import base64
import logging

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.db import transaction
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.shortcuts import redirect
from django.utils.decorators import method_decorator
from django.utils.translation import gettext_lazy as _
from django.views.decorators.cache import never_cache
from django.views.generic import DeleteView
from django.views.generic import ListView
from django.views.generic import View
from formtools.wizard.views import SessionWizardView

from classlab.apps.exceptions import QuotaExceededError
from classlab.apps.models import App
from classlab.apps.models import AppTemplateKeyValue

from .forms import CreateAppForm
from .forms import KeyValueConfigFormSet
from .forms import KeyValueConfigFormSetHelper

logger = logging.getLogger(__name__)

FORMS = [
    ("app", CreateAppForm),
    ("config", KeyValueConfigFormSet),
]

TEMPLATES = {
    "app": "apps/create.html",
    "config": "apps/create_config.html",
}


# condition that checks if config step should be shown
def condition_config(wizard):
    # Workaround to get the cleaned_data of the first step
    data = wizard.storage.data["step_data"]
    app_step_data = data.get("app", {})
    if not app_step_data:
        return False
    template = app_step_data.get("app-template", None)
    if template:
        template_id = template[0]
        return AppTemplateKeyValue.objects.filter(
            app_template__id=template_id,
            generated=False,
        ).exists()
    return False


def user_home(user):
    if user.is_authenticated:
        if user.is_teacher:
            return "teachers:home"
        elif user.is_student:  # noqa: RET505
            return "students:home"
        elif user.is_administrator:
            return "administrators:home"

    return "home"


@method_decorator(never_cache, name="dispatch")
class AppCreateWizard(LoginRequiredMixin, PermissionRequiredMixin, SessionWizardView):
    template_name = "apps/create.html"
    form_list = FORMS
    permission_required = "apps.add_app"
    condition_dict = {"config": condition_config}

    def get_template_names(self):
        return [TEMPLATES[self.steps.current]]

    def get_context_data(self, form, **kwargs):
        context = super().get_context_data(form=form, **kwargs)
        if self.steps.current == "config":
            context["helper"] = KeyValueConfigFormSetHelper()
        return context

    def get_form_kwargs(self, step):
        kwargs = super().get_form_kwargs(step)
        if step == "app":
            kwargs["user"] = self.request.user
        elif step == "config":
            kwargs["form_kwargs"] = {
                "instance": self.get_cleaned_data_for_step("app")["template"],
            }
        return kwargs

    def process_step(self, form):
        # if step app then set apptempalte in instance dict for config step
        if self.steps.current == "app":
            self.instance_dict["config"] = form.cleaned_data["template"]
        return super().process_step(form)

    def get_form_initial(self, step):
        initial = super().get_form_initial(step) or []
        if step == "config":
            template = self.get_cleaned_data_for_step("app")["template"]
            for key_value in template.key_values.filter(generated=False):
                data = {
                    "key": key_value.key,
                }
                initial.append(data)

        return initial

    def done(self, form_list, form_dict, **kwargs):
        template = form_dict["app"].cleaned_data["template"]
        name = form_dict["app"].cleaned_data["name"]
        app = App.objects.create(
            name=name,
            template=template,
            user=self.request.user,
            organisation=self.request.user.organisation,
        )
        try:
            config = {}

            if app.template.key_values.filter(generated=False).exists():
                for form in form_list[1]:
                    key = form.cleaned_data["key"]
                    kv = app.template.key_values.get(key=key)
                    if kv.secret:
                        config[key] = base64.b64encode(
                            form.cleaned_data["value"].encode(),
                        ).decode()
                    else:
                        config[key] = form.cleaned_data["value"]
            for kv in app.template.key_values.filter(generated=True):
                config[kv.key] = base64.b64encode(kv.generate().encode()).decode()

            transaction.on_commit(lambda: app.create(config))

            messages.success(self.request, _("App created successfully"))
        except Exception:
            logger.exception("Error creating app")
            messages.error(self.request, _("An error occurred while creating the app"))
            return redirect(user_home(self.request.user))

        return redirect(user_home(self.request.user))


class StartAppView(LoginRequiredMixin, PermissionRequiredMixin, View):
    """
    View get app_id and start app.
    """

    permission_required = "apps.start_app"

    def post(self, request, app_id):
        app = get_object_or_404(App, app_id=app_id)
        if app.user != request.user:
            messages.error(request, _("You don't have permission to do that"))
            return redirect(user_home(request.user))
        if app.managed_app:
            messages.error(request, _("App is managed"))
            return redirect(user_home(request.user))
        try:
            app.start()
            messages.success(request, _("App started successfully"))
            return JsonResponse({"status": "success"})
        except QuotaExceededError as e:
            logger.exception("Quota exceeded")
            return JsonResponse({"status": "error", "message": str(e)})


class AppStatusView(LoginRequiredMixin, PermissionRequiredMixin, View):
    """
    View get app_id and start app.
    """

    permission_required = "apps.view_app"

    def get(self, request, app_id):
        app = get_object_or_404(App, app_id=app_id, user=request.user)
        return JsonResponse(app.get_status())


class AppRunCommandView(LoginRequiredMixin, PermissionRequiredMixin, View):
    """
    View that returns app run command.
    """

    permission_required = "apps.view_app"

    def get(self, request, app_id):
        app = get_object_or_404(
            App,
            app_id=app_id,
            user=request.user,
            template__run_command_template__isnull=False,
        )
        return JsonResponse({"status": "success", "command": app.run_command})


class AppUrlView(LoginRequiredMixin, PermissionRequiredMixin, View):
    """
    View that returns app url.
    """

    permission_required = "apps.view_app"

    def get(self, request, app_id):
        app = get_object_or_404(App, app_id=app_id, user=request.user)
        try:
            return JsonResponse({"status": "success", "url": app.url})
        except Exception as e:
            logger.exception("Error getting app url")
            return JsonResponse({"status": "error", "message": str(e)})


class AppStopView(LoginRequiredMixin, PermissionRequiredMixin, View):
    """
    View get app_id and stop app.
    """

    permission_required = "apps.stop_app"

    def post(self, request, app_id):
        app = get_object_or_404(App, app_id=app_id)
        if app.user != request.user:
            messages.error(request, _("You don't have permission to do that"))
            return redirect(user_home(request.user))
        if app.managed_app:
            messages.error(request, _("App is managed"))
            return redirect(user_home(request.user))
        app.stop()
        return JsonResponse({"status": "success"})


class AppDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    """
    View to delete app.
    """

    model = App
    template_name = "apps/app_delete.html"
    success_url = "/"
    permission_required = "apps.delete_app"

    def get_object(self, queryset=None):
        if self.kwargs.get("app_id") is None:
            messages.error(self.request, _("App not found"))
            return redirect(user_home(self.request.user))

        obj = get_object_or_404(App, app_id=self.kwargs["app_id"], managed_app=None)
        if obj.user != self.request.user:
            messages.error(self.request, _("You don't have permission to do that"))
            return redirect(user_home(self.request.user))
        return obj


class AppListView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    """
    View to list all apps.
    """

    template_name = "apps/list.html"
    model = App
    context_object_name = "apps"
    permission_required = "apps.view_app"

    def get_queryset(self):
        return App.objects.filter(user=self.request.user)


# MANAGED


class StartManagedAppView(LoginRequiredMixin, PermissionRequiredMixin, View):
    """
    View get app_id and start app.
    """

    permission_required = "apps.start_app"

    def get(self, request, class_id, managed_app_id, app_id):
        app = get_object_or_404(App, app_id=app_id)
        if not app.managed_app:
            messages.error(request, _("App is not managed"))
            return redirect(user_home(request.user))

        # check if current user is teacher of managed app class
        if not app.managed_app.assigned_class.teachers.filter(
            id=request.user.teacher.id,
        ).exists():
            messages.error(request, _("You don't have permission to do that"))
            return redirect(user_home(request.user))

        try:
            app.start()
            messages.success(request, _("App started successfully"))
            return redirect(user_home(request.user))
        except QuotaExceededError as e:
            messages.error(request, str(e))
            return redirect(user_home(request.user))


class StopManagedAppView(LoginRequiredMixin, PermissionRequiredMixin, View):
    """
    View get app_id and stop app.
    """

    permission_required = "apps.stop_app"

    def get(self, request, class_id, managed_app_id, app_id):
        app = get_object_or_404(App, app_id=app_id)
        if not app.managed_app:
            messages.error(request, _("App is not managed"))
            return redirect(user_home(request.user))

        # check if current user is teacher of managed app class
        if not app.managed_app.assigned_class.teachers.filter(
            id=request.user.teacher.id,
        ).exists():
            messages.error(request, _("You don't have permission to do that"))
            return redirect(user_home(request.user))

        app.stop()
        messages.success(request, _("App stopped successfully"))
        return redirect(user_home(request.user))
