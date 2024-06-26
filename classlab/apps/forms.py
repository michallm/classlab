from crispy_forms.helper import FormHelper
from django import forms
from django.utils.translation import gettext_lazy as _

from .models import App
from .models import AppTemplate
from .models import AppTemplateKeyValue
from .models import ManagedApp


class AppTemplateKeyValueForm(forms.Form):
    key = forms.CharField(required=True, widget=forms.HiddenInput())
    value = forms.CharField(required=False)

    class Meta:
        model = AppTemplateKeyValue
        fields = ["key", "value"]
        readonly_fields = ["key"]

    def __init__(self, *args, instance, **kwargs):
        app_template = instance
        super().__init__(*args, **kwargs)
        self.instance = AppTemplateKeyValue.objects.get(
            app_template=app_template,
            key=self.initial["key"],
        )
        self.fields["value"].label = self.instance.name
        self.fields["value"].help_text = self.instance.description

        if self.instance.generated:
            self.fields["value"].widget.attrs["readonly"] = True
            self.Meta.readonly_fields.append("value")


KeyValueConfigFormSet = forms.formset_factory(
    AppTemplateKeyValueForm,
    extra=0,
    can_delete=False,
)


class KeyValueConfigFormSetHelper(FormHelper):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.form_tag = False
        self.form_class = "form-horizontal"
        self.label_class = "col-lg-4"
        self.field_class = "col-lg-8"


class CreateAppForm(forms.ModelForm):
    class Meta:
        model = App
        fields = ["template", "name"]

    def __init__(self, *args, **kwargs):
        if "user" in kwargs:
            self.user = kwargs.pop("user")
        super().__init__(*args, **kwargs)
        self.fields["template"].help_text = _(
            "Select the template for the app you want to create.",
        )
        self.fields["name"].help_text = _(
            "Enter a name for the app you want to create.",
        )
        self.fields["template"].queryset = AppTemplate.objects.filter(
            managed=False,
            organisations=self.user.organisation,
        )

    def clean_name(self):
        name = self.cleaned_data["name"]
        if App.objects.filter(name=name, user=self.user).exists():
            raise forms.ValidationError(
                _("An app with this name already exists for this user."),
            )
        return name

    def clean_template(self):
        # validate if template belongs to user organisation
        template = self.cleaned_data["template"]
        if self.user.organisation not in template.organisations.all():
            raise forms.ValidationError(
                _("You can only create apps from templates of your organisation."),
            )
        return template


class CreateManagedAppForm(forms.ModelForm):
    class Meta:
        model = ManagedApp
        fields = ["template", "name"]

    def __init__(self, *args, **kwargs):
        if "user" in kwargs:
            self.user = kwargs.pop("user")
        super().__init__(*args, **kwargs)
        self.fields["template"].help_text = _(
            "Select the template for the app you want to create.",
        )
        self.fields["name"].help_text = _(
            "Enter a name for the app you want to create.",
        )

        # filter templates that have a managed app already
        self.fields["template"].queryset = AppTemplate.objects.filter(
            managed=True,
            organisations=self.user.organisation,
        )

    def clean_template(self):
        # validate if template belongs to user organisation
        template = self.cleaned_data["template"]
        if self.user.organisation not in template.organisations.all():
            raise forms.ValidationError(
                _("You can only create apps from templates of your organisation."),
            )
        return template
