from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.shortcuts import get_object_or_404
from django.shortcuts import redirect
from django.urls import reverse
from django.views.generic import DeleteView
from django.views.generic import FormView
from django.views.generic import ListView
from django.views.generic import View

from classlab.classes.models import Class
from classlab.students.forms import StudentForm
from classlab.students.forms import StudentUpdateForm
from classlab.students.forms import StudentWithClassForm
from classlab.students.models import Student


class HomeView(LoginRequiredMixin, View):
    def get(self, request):
        return redirect("apps:list")


class StudentCreateView(LoginRequiredMixin, PermissionRequiredMixin, FormView):
    """
    View will accept a class_id path parameter and create a student for that class.
    """

    template_name = "students/create.html"
    form_class = StudentForm
    permission_required = "students.add_student"

    # check if class_id is valid
    def dispatch(self, request, *args, **kwargs):
        self.organisation = self.request.user.organisation
        self.class_ = get_object_or_404(
            Class,
            class_id=self.kwargs["class_id"],
            organisation=self.organisation,
        )
        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self):
        return reverse("classes:detail", kwargs={"class_id": self.class_.class_id})

    def form_valid(self, form):
        student = form.save(self.request, self.organisation, self.class_)
        if form.cleaned_data["send_email_confirmation"]:
            student.user.send_confirmation_email(self.request)
        return super().form_valid(form)


class StudentCreateWithClassView(LoginRequiredMixin, PermissionRequiredMixin, FormView):
    """
    View will create a student for a class.
    """

    template_name = "students/create_with_class.html"
    form_class = StudentWithClassForm
    permission_required = "students.add_student"

    def dispatch(self, request, *args, **kwargs):
        self.organisation = self.request.user.organisation
        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self):
        return reverse("students:list")

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["organisation"] = self.organisation
        return kwargs

    def form_valid(self, form):
        student = form.save(self.request, self.organisation)
        if form.cleaned_data["send_email_confirmation"]:
            student.user.send_confirmation_email(self.request)
        return super().form_valid(form)


class StudentListView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    model = Student
    template_name = "students/list.html"
    permission_required = "students.view_student"
    paginate_by = 15

    def get_queryset(self):
        return (
            super().get_queryset().filter(organisation=self.request.user.organisation)
        )


class StudentResendConfirmEmailView(LoginRequiredMixin, PermissionRequiredMixin, View):
    permission_required = "students.student_resend_confirm_email"

    def post(self, request, student_id):
        next_url = request.POST.get("next", None)
        student = get_object_or_404(
            Student,
            student_id=student_id,
            organisation=request.user.organisation,
        )
        student.user.send_confirmation_email(self.request)
        return redirect(next_url) if next_url else redirect("students:list")


class StudentDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    model = Student
    template_name = "students/delete.html"
    permission_required = "students.delete_student"

    def get_queryset(self):
        return (
            super().get_queryset().filter(organisation=self.request.user.organisation)
        )

    def get_success_url(self):
        return reverse("students:list")


class StudentUpdateView(LoginRequiredMixin, PermissionRequiredMixin, FormView):
    template_name = "students/update.html"
    form_class = StudentUpdateForm
    permission_required = "students.change_student"

    def dispatch(self, request, *args, **kwargs):
        self.student = get_object_or_404(
            Student,
            student_id=self.kwargs["student_id"],
            organisation=request.user.organisation,
        )
        return super().dispatch(request, *args, **kwargs)

    def get_initial(self):
        return {
            "first_name": self.student.user.first_name,
            "last_name": self.student.user.last_name,
            "email": self.student.user.email,
        }

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["student"] = self.student
        return kwargs

    def get_success_url(self):
        return reverse("students:list")

    def form_valid(self, form):
        form.save()
        return super().form_valid(form)
