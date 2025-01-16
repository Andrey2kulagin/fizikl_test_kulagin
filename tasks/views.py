from rest_framework import viewsets, permissions, status, filters
from rest_framework.response import Response
from rest_framework.decorators import action
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.pagination import PageNumberPagination
from .models import Task
from .serializers import TaskSerializer, TaskCreateSerializer
from .tasks import sum_task, countdown_task
from rest_framework import serializers


class TaskPagination(PageNumberPagination):
    """
    Кастомный класс пагинации.
    """
    page_size = 10  # Количество элементов на одной странице
    # Позволяет изменять размер страницы через query-параметр
    page_size_query_param = 'page_size'
    max_page_size = 100  # Максимальное количество элементов на странице


class TaskViewSet(viewsets.ModelViewSet):
    """
    ViewSet для управления задачами.
    """
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = TaskPagination  # Пагинация
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    http_method_names = ['get', 'head', 'options', 'post']

    # Фильтрация
    filterset_fields = ['status']  # Фильтр только по `status`

    # Сортировка
    ordering_fields = ['id']  # Сортировка только по `id`
    ordering = ['id']  # Сортировка по умолчанию (по возрастанию id)

    def get_queryset(self):
        """
        Ограничиваем видимость задач только для текущего пользователя.
        """
        return Task.objects.filter(user=self.request.user)

    def get_serializer_class(self):
        """
        Определяем, какой сериализатор использовать для различных действий.
        """
        if self.action == 'create':
            return TaskCreateSerializer
        return TaskSerializer

    def perform_create(self, serializer):
        """
        Создаем задачу и отправляем ее в Celery.
        """
        user = self.request.user
        # Ограничение на количество активных задач
        active_tasks_count = Task.objects.filter(
            user=user, status__in=['pending', 'in_progress']).count()
        if active_tasks_count >= 5:
            raise serializers.ValidationError(
                {"non_field_errors": ["Невозможно создать больше 5 задач одновременно."]})

        task = serializer.save(user=user, status='pending')

        # Отправка задачи в Celery
        if task.task_type == 'sum':
            sum_task.apply_async(args=[task.id])
        elif task.task_type == 'countdown':
            countdown_task.apply_async(args=[task.id])

        return task

    def create(self, request, *args, **kwargs):
        """
        Создаем задачу и возвращаем ID задачи.
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        task = self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)

        # Возвращаем ID задачи вместе с данными сериализатора
        return Response(
            {
                'id': task.id,
                'task_type': task.task_type,
                'input_data': task.input_data,
                'status': task.status,
                'result': task.result,
                'created_at': task.created_at,
            },
            status=status.HTTP_201_CREATED,
            headers=headers
        )

    @action(detail=True, methods=['get'])
    def result(self, request, pk=None):
        """
        Эндпоинт для получения результата конкретной задачи.
        """
        task = self.get_object()
        if task.user != request.user:
            return Response({'detail': 'Доступ запрещен.'}, status=status.HTTP_403_FORBIDDEN)
        return Response({'status': task.status, 'result': task.result})
