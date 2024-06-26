from allauth.account.utils import has_verified_email
from allauth.account.utils import sync_user_email_addresses
from django import forms
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _

from classlab.teachers.models import Teacher
from classlab.users.forms import HeadelessUserCreateForm

User = get_user_model()


class TeacherCreateForm(HeadelessUserCreateForm):
    send_email_confirmation = forms.BooleanField(
        label=_("Send email confirmation"),
        required=False,
        help_text=_("Send email confirmation to the user's email address."),
    )

    def save(self, request, organisation):
        user = super().save(request=request, user_type=User.UserType.TEACHER)
        return Teacher.objects.create(user=user, organisation=organisation)


class TeacherUpdateForm(forms.Form):
    first_name = forms.CharField(label=_("First name"))
    last_name = forms.CharField(label=_("Last name"))
    email = forms.EmailField(label=_("Email address"))

    def __init__(self, *args, teacher, **kwargs):
        self.teacher = teacher
        super().__init__(*args, **kwargs)

        # if email address is verified, then it cannot be changed
        if has_verified_email(self.teacher.user):
            self.fields["email"].disabled = True

    def clean_email(self):
        email = self.cleaned_data["email"]
        if email != self.teacher.user.email:
            if has_verified_email(self.teacher.user):
                raise forms.ValidationError(
                    _("Email address cannot be changed because it is verified."),
                )

            # if email address already exists, then it cannot be used

        return email

    def save(self):
        user = self.teacher.user
        user.first_name = self.cleaned_data["first_name"]
        user.last_name = self.cleaned_data["last_name"]

        if user.email != self.cleaned_data["email"]:
            user.email = self.cleaned_data["email"]
            user.emailaddress_set.all().delete()
            sync_user_email_addresses(user)

        user.save()

        return self.teacher
