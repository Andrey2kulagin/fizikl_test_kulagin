from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.response import Response
from rest_framework import viewsets
from user.models import CustomUser
from user.serializers import CustomUserSerializer, UserRegisterSerializer, CustomTokenObtainPairSerializer
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from rest_framework.views import APIView
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from rest_framework.permissions import AllowAny


    
class CustomUserViewSet(viewsets.ModelViewSet):
    queryset = CustomUser.objects.all()
    serializer_class = CustomUserSerializer
    permission_classes = [IsAuthenticated] 
    
    def get_queryset(self):
        # Возвращаем только данные текущего аутентифицированного пользователя
        user = self.request.user
        return CustomUser.objects.filter(id=user.id)
    
    def list(self, request, *args, **kwargs):
        """
        Возвращает данные только текущего пользователя, а не список.
        """
        user = self.request.user  # Получаем текущего пользователя
        serializer = self.get_serializer(user)  # Сериализуем объект пользователя
        return Response(serializer.data)  # Возвращаем сериализованные данные

    def retrieve(self, request, *args, **kwargs):
        """
        Возвращает данные текущего пользователя, игнорируя переданный pk.
        """
        user = self.request.user  # Получаем текущего пользователя
        serializer = self.get_serializer(user)  # Сериализуем объект пользователя
        return Response(serializer.data)  # Возвращаем сериализованные данные


    def create(self, request, *args, **kwargs):
        # Дополнительная логика перед созданием
        return super().create(request, *args, **kwargs)
    

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

class OpenAPIView(APIView):
    permission_classes = [AllowAny]  # Разрешаем доступ всем
    authentication_classes = []  # Не используем аутентификацию

    def get(self, request):
        return Response({"message": "This is an open endpoint!"})
class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer
