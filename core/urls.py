from django.contrib import admin
from django.urls import include, path
from user.admin import admin_site
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework_simplejwt.views import TokenRefreshView
from user.views import CustomTokenObtainPairView

schema_view = get_schema_view(
   openapi.Info(
      title="Task Management API",
      default_version='v1',
      description="API для создания и отслеживания задач",
      terms_of_service="https://www.google.com/policies/terms/",
      contact=openapi.Contact(email="contact@taskmanager.local"),
      license=openapi.License(name="BSD License"),
   ),
   public=True,  # Открывать для админов
)
urlpatterns = [
    path('admin/', admin_site.urls),
    path('api/token/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/', include('user.urls')),
    path('api/', include('tasks.urls')),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='swagger-ui'),
]
