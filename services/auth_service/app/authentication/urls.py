from authentication.views import (
    ChangePasswordAPIView,
    PublicTokenRefreshView,
    UserLoginAPIView,
    UserLogoutAPIView,
    UserMeAPIView,
    UserRegistrationAPIView,
)
from django.urls import path

app_name = "authentication"

urlpatterns = [
    path("register/", UserRegistrationAPIView.as_view(), name="register"),
    path("login/", UserLoginAPIView.as_view(), name="login"),
    path("logout/", UserLogoutAPIView.as_view(), name="logout"),
    path("me/", UserMeAPIView.as_view(), name="me"),
    path("change-password/", ChangePasswordAPIView.as_view(), name="change_password"),
    path("token/refresh/", PublicTokenRefreshView.as_view(), name="token_refresh"),
]
