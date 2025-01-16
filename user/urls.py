from django.urls import path, include
from rest_framework.routers import DefaultRouter
from user.views import CustomUserViewSet, RegisterView

# Создаём роутер для ViewSet
router = DefaultRouter()
router.register(r'user', CustomUserViewSet)

# Дополнительные маршруты
extra_patterns = [
    path('register/', RegisterView.as_view(), name='register'),
]

# Объединяем маршруты
urlpatterns = [
    path('', include(router.urls)),  # Все маршруты из DefaultRouter
    *extra_patterns,  # Дополнительные маршруты
]