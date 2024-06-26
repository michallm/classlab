from django.urls import path

from . import views

app_name = "teachers"

urlpatterns = [
    path(
        "",
        views.TeacherListView.as_view(),
        name="list",
    ),
    path(
        "create/",
        views.TeacherCreateView.as_view(),
        name="create",
    ),
    path(
        "home",
        view=views.HomeView.as_view(),
        name="home",
    ),
    path(
        "<str:teacher_id>/delete/",
        view=views.TeacherDeleteView.as_view(),
        name="delete",
    ),
    path(
        "<str:teacher_id>/update/",
        view=views.TeacherUpdateView.as_view(),
        name="update",
    ),
    path(
        "<str:teacher_id>/resend-confirm-email/",
        view=views.TeacherResendConfirmEmailView.as_view(),
        name="resend-confirm-email",
    ),
]
