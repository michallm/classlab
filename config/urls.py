from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include
from django.urls import path
from django.views import defaults as default_views

urlpatterns = [  # noqa: RUF005
    # Django Admin, use {% url 'admin:index' %}
    path(settings.ADMIN_URL, admin.site.urls),
    # User management
    path("users/", include("classlab.users.urls", namespace="users")),
    path("accounts/", include("classlab.accounts.urls")),
    path("i18n/", include("django.conf.urls.i18n")),
    # Your stuff: custom urls includes go here
    path("", include("classlab.core.urls")),
    path(
        "administrator/",
        include("classlab.administrators.urls", namespace="administrators"),
    ),
    path("apps/", include("classlab.apps.urls", namespace="apps")),
    path("student/", include("classlab.students.urls", namespace="students")),
    path("teacher/", include("classlab.teachers.urls", namespace="teachers")),
    path("class/", include("classlab.classes.urls", namespace="classes")),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if settings.DEBUG:
    # This allows the error pages to be debugged during development, just visit
    # these url in browser to see how these error pages look like.
    urlpatterns += [
        path("__reload__/", include("django_browser_reload.urls")),
        path(
            "400/",
            default_views.bad_request,
            kwargs={"exception": Exception("Bad Request!")},
        ),
        path(
            "403/",
            default_views.permission_denied,
            kwargs={"exception": Exception("Permission Denied")},
        ),
        path(
            "404/",
            default_views.page_not_found,
            kwargs={"exception": Exception("Page not Found")},
        ),
        path("500/", default_views.server_error),
    ]
    if "debug_toolbar" in settings.INSTALLED_APPS:
        import debug_toolbar

        urlpatterns = [path("__debug__/", include(debug_toolbar.urls)), *urlpatterns]
