from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect
from django.utils.translation import gettext_lazy as _


class UserOwnershipMixin(LoginRequiredMixin):
    """A mixin that checks that the user is the owner of the object"""

    def dispatch(self, request, *args, **kwargs):
        if self.get_object().user != request.user:
            messages.error(request, _("You don't have permission to do that"))
            return redirect("home")
        return super().dispatch(request, *args, **kwargs)
