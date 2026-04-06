from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken

User = get_user_model()


class RegistrationService:
    @staticmethod
    def register_user(*, email: str, username: str, password: str) -> User:
        return User.objects.create_user(
            email=email,
            username=username,
            password=password,
        )


class LoginService:
    @staticmethod
    def login_user(*, user: User) -> dict:
        refresh = RefreshToken.for_user(user)

        return {
            "access": str(refresh.access_token),
            "refresh": str(refresh),
            "user": {
                "id": user.id,
                "email": user.email,
                "username": user.username,
            },
        }


class LogoutService:
    @staticmethod
    def logout_user(*, refresh_token: str) -> None:
        token = RefreshToken(refresh_token)
        token.blacklist()


class ChangePasswordService:
    @staticmethod
    def change_password(*, user, new_password: str) -> None:
        user.set_password(new_password)
        user.save(update_fields=["password"])
