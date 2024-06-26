from django.urls import path

from classlab.users.views import user_detail_view
from classlab.users.views import user_redirect_view

app_name = "users"
urlpatterns = [
    path("~redirect/", view=user_redirect_view, name="redirect"),
    path("<str:user_id>/", view=user_detail_view, name="detail"),
]
