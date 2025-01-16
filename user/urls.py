from django.urls import path, include
from rest_framework.routers import DefaultRouter
from user.views import RegisterView, CustomTokenObtainPairView, CustomTokenRefreshView

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('token/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', CustomTokenRefreshView.as_view(), name='token_refresh'),
]
