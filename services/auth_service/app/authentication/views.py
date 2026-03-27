from authentication.serializers import (
    UserRegistrationResponseSerializer,
    UserRegistrationSerializer,
)
from authentication.services import RegistrationService
from rest_framework import status
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
