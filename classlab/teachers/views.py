from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.shortcuts import get_object_or_404
from django.shortcuts import redirect
from django.urls import reverse
from django.views.generic import DeleteView
from django.views.generic import FormView
from django.views.generic import ListView
from django.views.generic import View

from classlab.teachers.forms import TeacherCreateForm
from classlab.teachers.forms import TeacherUpdateForm
from classlab.teachers.models import Teacher

from .mixins import TeacherRequiredMixin


class HomeView(LoginRequiredMixin, TeacherRequiredMixin, View):
    def get(self, request):
        return redirect("apps:list")


class TeacherDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    """
    View will accept a teacher_id path parameter and delete the teacher.
    """

    model = Teacher
    template_name = "teachers/delete.html"
    permission_required = "teachers.delete_teacher"

    def get_success_url(self):
        return reverse("teachers:list")

    def get_queryset(self):
        return (
            super().get_queryset().filter(organisation=self.request.user.organisation)
        )

    def get_object(self, queryset=None):
        teacher_id = self.kwargs.get("teacher_id")
        return get_object_or_404(self.get_queryset(), teacher_id=teacher_id)

    def delete(self, request, *args, **kwargs):
        teacher = self.get_object()
        teacher.user.delete()
        return super().delete(request, *args, **kwargs)


class TeacherUpdateView(LoginRequiredMixin, PermissionRequiredMixin, FormView):
    """
    View will accept a teacher_id path parameter and update the teacher.
    """

    template_name = "teachers/update.html"
    form_class = TeacherUpdateForm
    permission_required = "teachers.change_teacher"

    def get_success_url(self):
        return reverse("teachers:list")

    def get_queryset(self):
        return Teacher.objects.filter(organisation=self.request.user.organisation)

    def get_object(self, queryset=None):
        teacher_id = self.kwargs.get("teacher_id")
        return get_object_or_404(self.get_queryset(), teacher_id=teacher_id)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["teacher"] = self.get_object()
        return kwargs

    def form_valid(self, form):
        form.save()
        return super().form_valid(form)

    def get_initial(self):
        teacher = self.get_object()
        return {
            "first_name": teacher.user.first_name,
            "last_name": teacher.user.last_name,
            "email": teacher.user.email,
        }


class TeacherResendConfirmEmailView(LoginRequiredMixin, PermissionRequiredMixin, View):
    """
    View will accept a teacher_id path parameter and resend the confirmation email.
    """

    permission_required = "teachers.teacher_resend_confirm_email"

    def post(self, request, teacher_id):
        teacher = get_object_or_404(
            Teacher,
            teacher_id=teacher_id,
            organisation=request.user.organisation,
        )
        teacher.user.send_confirmation_email(request)
        return redirect("teachers:list")


class TeacherListView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    model = Teacher
    template_name = "teachers/list.html"
    permission_required = "teachers.view_teacher"
    paginate_by = 15

    def get_queryset(self):
        return (
            super().get_queryset().filter(organisation=self.request.user.organisation)
        )


class TeacherCreateView(LoginRequiredMixin, PermissionRequiredMixin, FormView):
    template_name = "teachers/create.html"
    form_class = TeacherCreateForm
    permission_required = "teachers.add_teacher"

    def get_success_url(self):
        return reverse("teachers:list")

    def get_form_kwargs(self):
        return super().get_form_kwargs()

    def form_valid(self, form):
        teacher = form.save(self.request, self.request.user.organisation)
        if form.cleaned_data["send_email_confirmation"]:
            teacher.user.send_confirmation_email(self.request)
        return super().form_valid(form)
