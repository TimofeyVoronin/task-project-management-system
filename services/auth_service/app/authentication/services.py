from django.contrib.auth import get_user_model

User = get_user_model()


class RegistrationService:
    @staticmethod
    def register_user(*, email: str, username: str, password: str) -> User:
        return User.objects.create_user(
            email=email,
            username=username,
            password=password,
        )
