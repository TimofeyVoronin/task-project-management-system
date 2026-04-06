from authentication.views import UserLoginAPIView, UserRegistrationAPIView
from django.urls import path

app_name = "authentication"

urlpatterns = [
    path("register/", UserRegistrationAPIView.as_view(), name="register"),
    path("login/", UserLoginAPIView.as_view(), name="login"),
]
