from django.urls import path

from . import views

app_name = "students"

urlpatterns = [
    path("home", views.HomeView.as_view(), name="home"),
    path("create/<str:class_id>/", views.StudentCreateView.as_view(), name="create"),
    path(
        "create/",
        views.StudentCreateWithClassView.as_view(),
        name="create-with-class",
    ),
    path(
        "",
        views.StudentListView.as_view(),
        name="list",
    ),
    path(
        "<str:student_id>/resend-confirm-email/",
        views.StudentResendConfirmEmailView.as_view(),
        name="resend-confirm-email",
    ),
    path(
        "<str:student_id>/delete/",
        views.StudentDeleteView.as_view(),
        name="delete",
    ),
    path(
        "<str:student_id>/update/",
        views.StudentUpdateView.as_view(),
        name="update",
    ),
]
