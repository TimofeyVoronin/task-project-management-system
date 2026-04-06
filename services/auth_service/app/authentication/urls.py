from authentication.views import (
    UserLoginAPIView,
    UserLogoutAPIView,
    UserMeAPIView,
    UserRegistrationAPIView,
)
from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

app_name = "authentication"

urlpatterns = [
    path("register/", UserRegistrationAPIView.as_view(), name="register"),
    path("login/", UserLoginAPIView.as_view(), name="login"),
    path("logout/", UserLogoutAPIView.as_view(), name="logout"),
    path("me/", UserMeAPIView.as_view(), name="me"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
]
