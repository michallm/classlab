from allauth.account.utils import has_verified_email
from allauth.account.utils import sync_user_email_addresses
from crispy_forms.helper import FormHelper
from django import forms
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from django_select2 import forms as s2forms

from classlab.classes.models import Class
from classlab.students.models import Student
from classlab.users.forms import HeadelessUserCreateForm

User = get_user_model()


class StudentForm(HeadelessUserCreateForm):
    send_email_confirmation = forms.BooleanField(
        label=_("Send email confirmation"),
        required=False,
        help_text=_("Send email confirmation to the user's email address."),
    )

    def save(self, request, organisation, student_class):
        user = super().save(request=request, user_type=User.UserType.STUDENT)
        return Student.objects.create(
            user=user,
            student_class=student_class,
            organisation=organisation,
        )


class ClassSelectWidget(s2forms.ModelSelect2Widget):
    search_fields = [
        "name__icontains",
    ]

    def __init__(self, *args, **kwargs):
        kwargs["data_view"] = "select"
        super().__init__(*args, **kwargs)


class StudentWithClassForm(HeadelessUserCreateForm):
    student_class = forms.ModelChoiceField(
        queryset=Class.objects.none(),
        widget=ClassSelectWidget(
            attrs={
                "data-placeholder": _("Select class"),
                "data-minimum-input-length": 0,
            },
        ),
        required=True,
        label=_("Class"),
    )

    send_email_confirmation = forms.BooleanField(
        label=_("Send email confirmation"),
        required=False,
        help_text=_("Send email confirmation to the user's email address."),
    )

    def __init__(self, *args, organisation, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["student_class"].queryset = Class.objects.filter(
            organisation=organisation,
        )
        self.helper = FormHelper()
        self.helper.form_show_labels = False

    def save(self, request, organisation):
        user = super().save(request=request, user_type=User.UserType.STUDENT)
        student_class = self.cleaned_data["student_class"]

        return Student.objects.create(
            user=user,
            student_class=student_class,
            organisation=organisation,
        )


class StudentUpdateForm(forms.Form):
    first_name = forms.CharField(label=_("First name"), max_length=30)
    last_name = forms.CharField(label=_("Last name"), max_length=150)
    email = forms.EmailField(label=_("Email address"))

    def __init__(self, *args, student, **kwargs):
        self.student = student
        super().__init__(*args, **kwargs)

        # if email address is verified, then it cannot be changed
        if has_verified_email(self.student.user):
            self.fields["email"].disabled = True

    def clean_email(self):
        email = self.cleaned_data["email"]
        if email != self.student.user.email:
            if has_verified_email(self.student.user):
                raise forms.ValidationError(
                    _("Email address cannot be changed because it is verified."),
                )

            # if email address already exists, then it cannot be used

        return email

    def save(self):
        user = self.student.user
        user.first_name = self.cleaned_data["first_name"]
        user.last_name = self.cleaned_data["last_name"]

        if user.email != self.cleaned_data["email"]:
            user.email = self.cleaned_data["email"]
            user.emailaddress_set.all().delete()
            sync_user_email_addresses(user)

        user.save()
        return user
