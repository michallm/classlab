import pytest
from django.conf import settings
from django.contrib.auth.models import AnonymousUser
from django.http import HttpResponseRedirect
from django.test import RequestFactory
from django.urls import reverse

from classlab.users.models import User
from classlab.users.tests.factories import UserFactory
from classlab.users.views import UserRedirectView
from classlab.users.views import user_detail_view

pytestmark = pytest.mark.django_db


class TestUserRedirectView:
    def test_get_redirect_url(self, user: User, rf: RequestFactory):
        view = UserRedirectView()
        request = rf.get("/fake-url")
        request.user = user

        view.request = request

        assert view.get_redirect_url() == "/"


class TestUserDetailView:
    def test_authenticated(self, user: User, rf: RequestFactory):
        request = rf.get("/fake-url/")
        request.user = UserFactory()

        response = user_detail_view(request, pk=user.pk)

        assert response.status_code == 200  # noqa: PLR2004

    def test_not_authenticated(self, user: User, rf: RequestFactory):
        request = rf.get("/fake-url/")
        request.user = AnonymousUser()

        response = user_detail_view(request, username=user.pk)
        login_url = reverse(settings.LOGIN_URL)

        assert isinstance(response, HttpResponseRedirect)
        assert response.status_code == 302  # noqa: PLR2004
        assert response.url == f"{login_url}?next=/fake-url/"
