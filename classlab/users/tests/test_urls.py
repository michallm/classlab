from django.urls import resolve
from django.urls import reverse

from classlab.users.models import User


def test_detail(user: User):
    assert (
        reverse("users:detail", kwargs={"user_id": user.user_id})
        == f"/users/{user.user_id}/"
    )
    assert resolve(f"/users/{user.user_id}/").view_name == "users:detail"


def test_redirect():
    assert reverse("users:redirect") == "/users/~redirect/"
    assert resolve("/users/~redirect/").view_name == "users:redirect"
