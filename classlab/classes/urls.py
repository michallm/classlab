from django.urls import path

from classlab.apps.views import StartManagedAppView
from classlab.apps.views import StopManagedAppView

from . import views

app_name = "classes"

urlpatterns = [
    path("", views.ClassListView.as_view(), name="list"),
    path("create/", views.ClassCreateView.as_view(), name="create"),
    path("<str:class_id>/", views.ClassDetailView.as_view(), name="detail"),
    path(
        "<str:class_id>/delete/",
        views.ClassDeleteView.as_view(),
        name="delete",
    ),
    path(
        "<str:class_id>/update/",
        views.ClassUpdateView.as_view(),
        name="update",
    ),
    path(
        "<str:class_id>/apps/create/",
        views.ClassCreateManagedAppWizard.as_view(),
        name="create_app",
    ),
    path(
        "<str:class_id>/apps/<str:managed_app_id>/",
        views.ClassDetailManagedAppView.as_view(),
        name="detail_app",
    ),
    path(
        "<str:class_id>/apps/<str:managed_app_id>/delete/",
        views.ClassDeleteManagedAppView.as_view(),
        name="delete_app",
    ),
    path(
        "<str:class_id>/apps/<str:managed_app_id>/start/<str:app_id>/",
        StartManagedAppView.as_view(),
        name="start_app",
    ),
    path(
        "<str:class_id>/apps/<str:managed_app_id>/stop/<str:app_id>/",
        StopManagedAppView.as_view(),
        name="stop_app",
    ),
]
