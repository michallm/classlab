from django.urls import path

from . import views

app_name = "apps"

urlpatterns = [
    path(
        "",
        views.AppListView.as_view(),
        name="list",
    ),
    path(
        "create/",
        views.AppCreateWizard.as_view(),
        name="create",
    ),
    path(
        "<str:app_id>/start/",
        views.StartAppView.as_view(),
        name="start",
    ),
    path(
        "<str:app_id>/delete/",
        views.AppDeleteView.as_view(),
        name="delete",
    ),
    path("<str:app_id>/stop/", views.AppStopView.as_view(), name="stop"),
    path("<str:app_id>/status/", views.AppStatusView.as_view(), name="status"),
    path(
        "<str:app_id>/run-command/",
        views.AppRunCommandView.as_view(),
        name="run-command",
    ),
    path("<str:app_id>/url/", views.AppUrlView.as_view(), name="url"),
]
