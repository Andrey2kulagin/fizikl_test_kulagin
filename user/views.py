from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework.response import Response
from user.serializers import UserRegisterSerializer, CustomTokenObtainPairSerializer
from rest_framework import status
from rest_framework.views import APIView
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from rest_framework.permissions import AllowAny


class RegisterView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []

    @swagger_auto_schema(
        request_body=UserRegisterSerializer,
        responses={
            201: openapi.Response("User registered successfully"),
            400: openapi.Response("Validation errors"),
        },
    )
    def post(self, request, *args, **kwargs):
        """
        User registration endpoint.
        """
        serializer = UserRegisterSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "User registered successfully"}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CustomTokenObtainPairView(TokenObtainPairView):
    permission_classes = [AllowAny]
    serializer_class = CustomTokenObtainPairSerializer


class CustomTokenRefreshView(TokenRefreshView):
    permission_classes = [AllowAny]
