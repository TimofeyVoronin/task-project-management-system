from authentication.serializers import (
    UserLoginResponseSerializer,
    UserLoginSerializer,
    UserLogoutSerializer,
    UserMeSerializer,
    UserRegistrationResponseSerializer,
    UserRegistrationSerializer,
)
from authentication.services import LoginService, LogoutService, RegistrationService
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


class UserLogoutAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        input_serializer = UserLogoutSerializer(data=request.data)
        input_serializer.is_valid(raise_exception=True)

        LogoutService.logout_user(
            refresh_token=input_serializer.validated_data["refresh"]
        )

        return Response(status=status.HTTP_204_NO_CONTENT)
