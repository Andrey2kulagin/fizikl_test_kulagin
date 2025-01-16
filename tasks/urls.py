from rest_framework.routers import DefaultRouter
from tasks.views import TaskViewSet

router = DefaultRouter()
router.register(r'task', TaskViewSet)


urlpatterns = router.urls  # Просто передаем маршруты из роутера