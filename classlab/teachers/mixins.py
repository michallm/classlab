# mixin that  allows only access to teachers
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import UserPassesTestMixin
from django.shortcuts import redirect
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

User = get_user_model()


class TeacherRequiredMixin(UserPassesTestMixin):
    """
    Mixin that  allows only access to teachers
    """

    def test_func(self):
        return self.request.user.user_type == User.UserType.TEACHER

    def handle_no_permission(self):
        messages.error(self.request, _("You are not allowed to access this page."))
        return redirect(reverse("home"))
