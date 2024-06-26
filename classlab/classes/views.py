import base64
from venv import logger

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.core.exceptions import PermissionDenied
from django.db.models import Count
from django.shortcuts import get_object_or_404
from django.shortcuts import redirect
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.utils.translation import gettext_lazy as _
from django.views.decorators.cache import never_cache
from django.views.generic import DeleteView
from django.views.generic import DetailView
from django.views.generic import FormView
from django.views.generic import ListView
from django.views.generic import UpdateView
from formtools.wizard.views import SessionWizardView

from classlab.apps.forms import CreateManagedAppForm
from classlab.apps.forms import KeyValueConfigFormSet
from classlab.apps.forms import KeyValueConfigFormSetHelper
from classlab.apps.models import App
from classlab.apps.models import ManagedApp
from classlab.apps.views import condition_config
from classlab.classes.forms import ClassForm
from classlab.classes.models import Class


class ClassListView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    model = Class
    template_name = "classes/list.html"
    permission_required = "classes.view_class"
    paginate_by = 10

    def get_queryset(self):
        qs = (
            super()
            .get_queryset()
            .filter(organisation=self.request.user.organisation)
            .annotate(students_count=Count("students"))
            .order_by("name")
        )
        if self.request.user.is_teacher:
            qs = qs.filter(teachers=self.request.user.teacher)
        return qs


class ClassCreateView(LoginRequiredMixin, PermissionRequiredMixin, FormView):
    template_name = "classes/create.html"
    form_class = ClassForm
    permission_required = "classes.add_class"

    def get_success_url(self):
        return reverse("classes:list")

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["organisation"] = self.request.user.organisation
        return kwargs

    def form_valid(self, form):
        form.save()
        return super().form_valid(form)


class ClassDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    """
    View will accept a class_id path parameter and delete the class.
    """

    model = Class
    template_name = "classes/delete.html"
    permission_required = "classes.delete_class"

    def get_object(self, queryset=None):
        obj = get_object_or_404(
            Class,
            class_id=self.kwargs["class_id"],
            organisation=self.request.user.organisation,
        )

        if self.request.user.is_teacher:
            if not obj.teachers.filter(pk=self.request.user.teacher.pk).exists():
                raise PermissionDenied

        return obj

    def get_success_url(self):
        return reverse("classes:list")


class ClassUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    """
    View will accept a class_id path parameter and update the class.
    """

    model = Class
    template_name = "classes/update.html"
    form_class = ClassForm
    permission_required = "classes.change_class"

    def get_object(self, queryset=None):
        obj = get_object_or_404(
            Class,
            class_id=self.kwargs["class_id"],
            organisation=self.request.user.organisation,
        )

        if self.request.user.is_teacher:
            if not obj.teachers.filter(pk=self.request.user.teacher.pk).exists():
                raise PermissionDenied

        return obj

    def get_success_url(self):
        return reverse("classes:list")

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["organisation"] = self.request.user.organisation

        return kwargs


class ClassDetailView(LoginRequiredMixin, PermissionRequiredMixin, DetailView):
    """
    View will accept a class_id path parameter and display the class.
    """

    model = Class
    template_name = "classes/detail.html"
    permission_required = "classes.view_class"

    def get_object(self, queryset=None):
        obj = get_object_or_404(
            Class,
            class_id=self.kwargs["class_id"],
            organisation=self.request.user.organisation,
        )

        if self.request.user.is_teacher:
            if not obj.teachers.filter(pk=self.request.user.teacher.pk).exists():
                raise PermissionDenied

        return obj

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["students"] = self.object.students.all()
        context["apps"] = ManagedApp.objects.filter(assigned_class=self.object)
        return context


FORMS = [
    ("app", CreateManagedAppForm),
    ("config", KeyValueConfigFormSet),
]

TEMPLATES = {
    "app": "apps/create_managed.html",
    "config": "apps/create_config.html",
}


@method_decorator(never_cache, name="dispatch")
class ClassCreateManagedAppWizard(
    LoginRequiredMixin,
    PermissionRequiredMixin,
    SessionWizardView,
):
    template_name = "apps/create_managed.html"
    form_list = FORMS
    permission_required = "apps.add_managedapp"
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
        class_id = self.request.resolver_match.kwargs["class_id"]
        class_obj = get_object_or_404(
            Class,
            class_id=class_id,
            organisation=self.request.user.organisation,
        )
        managed_app = ManagedApp.objects.create(
            name=name,
            template=template,
            organisation=self.request.user.organisation,
            assigned_class=class_obj,
        )

        try:
            shared_config = {}

            if managed_app.template.key_values.filter(generated=False).exists():
                for form in form_list[1]:
                    key = form.cleaned_data["key"]
                    kv = managed_app.template.key_values.get(key=key)
                    if kv.secret:
                        shared_config[key] = base64.b64encode(
                            form.cleaned_data["value"].encode(),
                        ).decode()
                    else:
                        shared_config[key] = form.cleaned_data["value"]
            for kv in template.key_values.filter(generated=True, student_only=False):
                if kv.generator == "username":
                    generated_value = kv.generate(self.request.user.first_name)
                else:
                    generated_value = kv.generate()

                shared_config[kv.key] = base64.b64encode(
                    generated_value.encode(),
                ).decode()

            for student in class_obj.students.all():
                config = shared_config.copy()
                for kv in template.key_values.filter(generated=True, student_only=True):
                    if kv.generator == "username":
                        generated_value = kv.generate(student.user.first_name)
                    else:
                        generated_value = kv.generate()

                    config[kv.key] = base64.b64encode(generated_value.encode()).decode()

                app = App.objects.create(
                    name=name,
                    template=template,
                    user=student.user,
                    organisation=self.request.user.organisation,
                    managed_app=managed_app,
                )
                app.create(config)
        except Exception as e:  # noqa: BLE001
            logger.exception("Failed to create app: %s", e)
            managed_app.delete()
            messages.error(
                self.request,
                _("An error occurred while creating the app. Please try again later."),
            )
            return redirect("classes:detail", class_id=class_id)

        messages.success(
            self.request,
            _("The app was successfully created."),
        )

        return redirect("classes:detail", class_id=class_id)


class ClassDeleteManagedAppView(
    LoginRequiredMixin,
    PermissionRequiredMixin,
    DeleteView,
):
    """
    View will accept a class_id path parameter and delete the class.
    """

    model = ManagedApp
    template_name = "apps/delete_managed.html"
    permission_required = "apps.delete_managedapp"

    def get_object(self, queryset=None):
        obj = get_object_or_404(
            ManagedApp,
            managed_app_id=self.kwargs["managed_app_id"],
            organisation=self.request.user.organisation,
        )

        if self.request.user.is_teacher:
            if not obj.assigned_class.teachers.filter(
                pk=self.request.user.teacher.pk,
            ).exists():
                raise PermissionDenied

        return obj

    def get_success_url(self):
        return reverse(
            "classes:detail",
            kwargs={"class_id": self.object.assigned_class.class_id},
        )


class ClassDetailManagedAppView(
    LoginRequiredMixin,
    PermissionRequiredMixin,
    DetailView,
):
    """
    View will accept a class_id path parameter and display the class.
    """

    model = ManagedApp
    template_name = "apps/detail_managed.html"
    permission_required = "apps.view_managedapp"

    def get_object(self, queryset=None):
        obj = get_object_or_404(
            ManagedApp,
            managed_app_id=self.kwargs["managed_app_id"],
            organisation=self.request.user.organisation,
        )

        if self.request.user.is_teacher:
            if not obj.assigned_class.teachers.filter(
                pk=self.request.user.teacher.pk,
            ).exists():
                raise PermissionDenied

        return obj

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["apps"] = App.objects.filter(managed_app=self.object)
        return context
