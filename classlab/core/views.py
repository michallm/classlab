from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect
from django.utils.translation import gettext_lazy as _
from django.views.generic import FormView
from django.views.generic import TemplateView
from django_select2.views import AutoResponseView

from .forms import ContactForm


class HomeView(FormView):
    template_name = "core/home.html"
    form_class = ContactForm
    success_url = "/"

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            if request.user.is_administrator:
                return redirect("administrators:home")
            elif request.user.is_teacher:  # noqa: RET505
                return redirect("teachers:home")
            elif request.user.is_student:
                return redirect("students:home")
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        form.send_email()
        messages.success(self.request, _("Message sent successfully"))
        return redirect(self.success_url)


class PrivacyPolicyView(TemplateView):
    template_name = "core/privacy_policy.html"


class TermsOfServiceView(TemplateView):
    template_name = "core/terms_of_service.html"


class Select2View(LoginRequiredMixin, AutoResponseView):
    def get_queryset(self):
        qs = super().get_queryset()
        return qs.filter(organisation=self.request.user.organisation)
