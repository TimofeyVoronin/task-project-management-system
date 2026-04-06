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
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView


class UserRegistrationAPIView(APIView):
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
    def post(self, request):
        input_serializer = UserLoginSerializer(
            data=request.data,
            context={"request": request},
        )
        input_serializer.is_valid(raise_exception=True)

        result = LoginService.login_user(user=input_serializer.validated_data["user"])

        output_serializer = UserLoginResponseSerializer(result)

        return Response(
            output_serializer.data,
            status=status.HTTP_200_OK,
        )


class UserMeAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        output_serializer = UserMeSerializer(request.user)
        return Response(output_serializer.data, status=status.HTTP_200_OK)

    def patch(self, request):
        input_serializer = UserProfileUpdateSerializer(
            request.user,
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
