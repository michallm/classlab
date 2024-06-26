from django import forms
from django.core.mail import send_mail
from django.utils.translation import gettext_lazy as _


class ContactForm(forms.Form):
    name = forms.CharField(max_length=100, label=_("Name"))
    email = forms.EmailField(label=_("Email"))
    message = forms.CharField(widget=forms.Textarea, label=_("Message"))

    def send_email(self):
        name = self.cleaned_data["name"]
        email = self.cleaned_data["email"]
        message = self.cleaned_data["message"]
        message = f"From: {name} ({email})\n\n{message}"
        send_mail(
            "ClassLab Contact Form",
            message,
            "kontakt@classlab.pl",
            ["kontakt@classlab.pl"],
            fail_silently=False,
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["name"].widget.attrs["placeholder"] = _("Enter your name")
        self.fields["email"].widget.attrs["placeholder"] = _("Enter your email")
        self.fields["message"].widget.attrs["placeholder"] = _("Type your message")
