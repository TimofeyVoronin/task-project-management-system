from authentication.views import UserRegistrationAPIView
from django.urls import path

app_name = "authentication"

urlpatterns = [
    path("register/", UserRegistrationAPIView.as_view(), name="register"),
]
