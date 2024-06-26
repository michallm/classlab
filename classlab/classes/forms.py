from crispy_forms.helper import FormHelper
from django import forms
from django.utils.translation import gettext_lazy as _
from django_select2 import forms as s2forms

from classlab.classes.models import Class
from classlab.teachers.models import Teacher


class TeachersSelect2Widget(s2forms.ModelSelect2MultipleWidget):
    search_fields = ["user__first_name__icontains", "user__last_name__icontains"]

    def __init__(self, *args, **kwargs):
        kwargs["data_view"] = "select"
        super().__init__(*args, **kwargs)

    def label_from_instance(self, obj):
        return obj.user.get_full_name()


class ClassForm(forms.ModelForm):
    teachers = forms.ModelMultipleChoiceField(
        queryset=Teacher.objects.none(),
        widget=TeachersSelect2Widget(
            attrs={
                "data-placeholder": _("Select teachers"),
                "data-minimum-input-length": 0,
            },
        ),
        required=False,
        label=_("Teachers"),
    )

    class Meta:
        model = Class
        fields = ["name", "teachers"]

    def __init__(self, *args, **kwargs):
        self.organisation = kwargs.pop("organisation")
        super().__init__(*args, **kwargs)
        if self.instance.pk:
            self.fields["teachers"].initial = self.instance.teachers.all()
        self.fields["teachers"].queryset = Teacher.objects.filter(
            organisation=self.organisation,
        )
        self.helper = FormHelper()
        self.helper.form_show_labels = False

    def save(self, *, commit=True):
        instance = super().save(commit=False)
        instance.organisation = self.organisation
        if commit:
            instance.save()
            instance.teachers.set(self.cleaned_data["teachers"])
            self.save_m2m()
        return instance
