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
from drf_spectacular.utils import OpenApiExample, OpenApiResponse, extend_schema
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenRefreshView


class UserRegistrationAPIView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
        auth=None,
        tags=["Authentication"],
        summary="Register a new user",
        description="Creates a new user account in the auth service.",
        request=UserRegistrationSerializer,
        responses={
            201: UserRegistrationResponseSerializer,
            400: OpenApiResponse(description="Validation error"),
        },
        examples=[
            OpenApiExample(
                "Register request",
                value={
                    "email": "user@example.com",
                    "username": "new_user",
                    "password": "StrongPass123!",
                },
                request_only=True,
            ),
            OpenApiExample(
                "Register success response",
                value={
                    "id": 1,
                    "email": "user@example.com",
                    "username": "new_user",
                    "is_active": True,
                    "created_at": "2026-04-07T10:00:00Z",
                },
                response_only=True,
                status_codes=["201"],
            ),
        ],
    )
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

    @extend_schema(
        auth=None,
        tags=["Authentication"],
        summary="Login user",
        description=(
            "Authenticates a user by email and password and returns access "
            "and refresh JWT tokens."
        ),
        request=UserLoginSerializer,
        responses={
            200: UserLoginResponseSerializer,
            400: OpenApiResponse(description="Invalid credentials or validation error"),
        },
        examples=[
            OpenApiExample(
                "Login request",
                value={
                    "email": "user@example.com",
                    "password": "StrongPass123!",
                },
                request_only=True,
            ),
            OpenApiExample(
                "Login success response",
                value={
                    "access": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.access",
                    "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.refresh",
                    "user": {
                        "id": 1,
                        "email": "user@example.com",
                        "username": "new_user",
                    },
                },
                response_only=True,
                status_codes=["200"],
            ),
        ],
    )
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

    @extend_schema(
        tags=["Authentication"],
        summary="Get current user profile",
        description="Returns the authenticated user's profile.",
        responses={
            200: UserMeSerializer,
            401: OpenApiResponse(
                description="Authentication credentials were not provided"
            ),
            403: OpenApiResponse(description="Permission denied"),
        },
    )
    def get(self, request):
        user = self.get_object()
        output_serializer = UserMeSerializer(user)
        return Response(output_serializer.data, status=status.HTTP_200_OK)

    @extend_schema(
        tags=["Authentication"],
        summary="Update current user profile",
        description="Partially updates the authenticated user's profile.",
        request=UserProfileUpdateSerializer,
        responses={
            200: UserMeSerializer,
            400: OpenApiResponse(description="Validation error"),
            401: OpenApiResponse(
                description="Authentication credentials were not provided"
            ),
            403: OpenApiResponse(description="Permission denied"),
        },
        examples=[
            OpenApiExample(
                "Update profile request",
                value={
                    "email": "updated@example.com",
                    "username": "updated_user",
                },
                request_only=True,
            ),
            OpenApiExample(
                "Update profile success response",
                value={
                    "id": 1,
                    "email": "updated@example.com",
                    "username": "updated_user",
                    "is_active": True,
                    "created_at": "2026-04-07T10:00:00Z",
                },
                response_only=True,
                status_codes=["200"],
            ),
        ],
    )
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

    @extend_schema(
        tags=["Authentication"],
        summary="Logout user",
        description=(
            "Blacklists the provided refresh token and invalidates future "
            "refresh attempts."
        ),
        request=UserLogoutSerializer,
        responses={
            204: OpenApiResponse(description="Logout successful"),
            400: OpenApiResponse(description="Validation error"),
            401: OpenApiResponse(
                description="Authentication credentials were not provided"
            ),
        },
        examples=[
            OpenApiExample(
                "Logout request",
                value={
                    "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.refresh",
                },
                request_only=True,
            ),
        ],
    )
    def post(self, request):
        input_serializer = UserLogoutSerializer(data=request.data)
        input_serializer.is_valid(raise_exception=True)

        LogoutService.logout_user(
            refresh_token=input_serializer.validated_data["refresh"]
        )

        return Response(status=status.HTTP_204_NO_CONTENT)


class ChangePasswordAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=["Authentication"],
        summary="Change password",
        description=(
            "Changes the authenticated user's password after verifying "
            "the old password."
        ),
        request=ChangePasswordSerializer,
        responses={
            200: OpenApiResponse(description="Password changed successfully"),
            400: OpenApiResponse(description="Validation error"),
            401: OpenApiResponse(
                description="Authentication credentials were not provided"
            ),
        },
        examples=[
            OpenApiExample(
                "Change password request",
                value={
                    "old_password": "StrongPass123!",
                    "new_password": "NewStrongPass123!",
                    "new_password_confirm": "NewStrongPass123!",
                },
                request_only=True,
            ),
            OpenApiExample(
                "Change password success response",
                value={
                    "detail": "Password changed successfully.",
                },
                response_only=True,
                status_codes=["200"],
            ),
        ],
    )
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

    @extend_schema(
        auth=None,
        tags=["Authentication"],
        summary="Refresh access token",
        description="Returns a new access token for a valid refresh token.",
        examples=[
            OpenApiExample(
                "Refresh token request",
                value={
                    "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.refresh",
                },
                request_only=True,
            ),
            OpenApiExample(
                "Refresh token success response",
                value={
                    "access": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.access",
                },
                response_only=True,
                status_codes=["200"],
            ),
        ],
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)
