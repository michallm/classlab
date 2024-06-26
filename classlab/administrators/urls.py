from django.urls import path

from . import views

app_name = "administrators"

urlpatterns = [
    path("", views.AdministratorHomeView.as_view(), name="home"),
    path("dashboard/", views.AdministratorDashboardView.as_view(), name="dashboard"),
    path(
        "dashboard/resources/cpu/",
        views.CPUResourceView.as_view(),
        name="cpu_resources",
    ),
    path(
        "dashboard/resources/memory/",
        views.MemoryResourceView.as_view(),
        name="memory_resources",
    ),
    path(
        "dashboard/resources/storage/",
        views.StorageResourceView.as_view(),
        name="storage_resources",
    ),
]
