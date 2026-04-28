from django.urls import path
from rest_framework.authtoken.views import obtain_auth_token

from accounts.views import RegisterView

urlpatterns = [
    path("register/", RegisterView.as_view(), name="register"),
    path("login/", obtain_auth_token, name="login"),
]
