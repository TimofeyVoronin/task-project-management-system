from authentication.permissions import IsOwner
from authentication.serializers import (
    ChangePasswordSerializer,
    UserLoginResponseSerializer,
    UserLoginSerializer,
    UserLogoutSerializer,
    UserMeSerializer,
    UserProfileUpdateSerializer,
    UserRegistrationResponseSerializer,
    UserRegistrationSerializer,
)
from authentication.services import (
    ChangePasswordService,
    LoginService,
    LogoutService,
    RegistrationService,
)
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenRefreshView


class UserRegistrationAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        input_serializer = UserRegistrationSerializer(data=request.data)
        input_serializer.is_valid(raise_exception=True)

        user = RegistrationService.register_user(**input_serializer.validated_data)

        output_serializer = UserRegistrationResponseSerializer(user)

        return Response(
            output_serializer.data,
            status=status.HTTP_201_CREATED,
        )


class UserLoginAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        input_serializer = UserLoginSerializer(
            data=request.data,
            context={"request": request},
        )
        input_serializer.is_valid(raise_exception=True)

        ip_address = request.META.get("REMOTE_ADDR")
        user_agent = request.META.get("HTTP_USER_AGENT", "")

        result = LoginService.login_user(
            user=input_serializer.validated_data["user"],
            ip_address=ip_address,
            user_agent=user_agent,
        )

        output_serializer = UserLoginResponseSerializer(result)

        return Response(
            output_serializer.data,
            status=status.HTTP_200_OK,
        )


class UserMeAPIView(APIView):
    permission_classes = [IsAuthenticated, IsOwner]

    def get_object(self):
        obj = self.request.user
        self.check_object_permissions(self.request, obj)
        return obj

    def get(self, request):
        user = self.get_object()
        output_serializer = UserMeSerializer(user)
        return Response(output_serializer.data, status=status.HTTP_200_OK)

    def patch(self, request):
        user = self.get_object()

        input_serializer = UserProfileUpdateSerializer(
            user,
            data=request.data,
            partial=True,
        )
        input_serializer.is_valid(raise_exception=True)
        user = input_serializer.save()

        output_serializer = UserMeSerializer(user)
        return Response(output_serializer.data, status=status.HTTP_200_OK)


class UserLogoutAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        input_serializer = UserLogoutSerializer(data=request.data)
        input_serializer.is_valid(raise_exception=True)

        LogoutService.logout_user(
            refresh_token=input_serializer.validated_data["refresh"]
        )

        return Response(status=status.HTTP_204_NO_CONTENT)


class ChangePasswordAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        input_serializer = ChangePasswordSerializer(
            data=request.data,
            context={"request": request},
        )
        input_serializer.is_valid(raise_exception=True)

        ChangePasswordService.change_password(
            user=request.user,
            new_password=input_serializer.validated_data["new_password"],
        )

        return Response(
            {"detail": "Password changed successfully."},
            status=status.HTTP_200_OK,
        )


class PublicTokenRefreshView(TokenRefreshView):
    permission_classes = [AllowAny]
