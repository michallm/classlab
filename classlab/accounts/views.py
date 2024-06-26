import logging

from allauth.account.adapter import get_adapter
from allauth.account.utils import user_pk_to_url_str
from allauth.account.views import ConfirmEmailView as BaseConfirmEmailView
from allauth.account.views import PasswordSetView as BasePasswordSetView
from django.urls import reverse

logger = logging.getLogger(__name__)


class ConfirmEmailView(BaseConfirmEmailView):
    def login_on_confirm(self, confirmation):
        adapter = get_adapter(self.request)
        user = confirmation.email_address.user
        logger.debug("login_on_confirm: %s", user)
        if not user.has_usable_password():
            logger.debug("login_on_confirm: %s has no password", user)
            adapter.stash_user(self.request, user_pk_to_url_str(user))

        return super().login_on_confirm(confirmation)


confirm_email = ConfirmEmailView.as_view()


class PasswordSetView(BasePasswordSetView):
    def get_success_url(self):
        return reverse("users:detail", kwargs={"user_id": self.request.user.user_id})


password_set = PasswordSetView.as_view()
