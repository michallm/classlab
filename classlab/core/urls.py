from django.urls import path
from django.urls import reverse_lazy
from django.views.generic import RedirectView

from .views import Select2View
from .views import TemplateView

urlpatterns = [
    path("", RedirectView.as_view(url=reverse_lazy("account_login"))),
    path("select/", Select2View.as_view(), name="select"),
    path(
        "robots.txt",
        TemplateView.as_view(
            template_name="core/robots.txt",
            content_type="text/plain",
        ),
    ),
]
