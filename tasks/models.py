
from django.db import models
from django.contrib.auth import get_user_model
import json

User = get_user_model()

class Task(models.Model):
    TASK_TYPES = [
        ('sum', 'Сумма двух чисел'),
        ('countdown', 'Обратный отсчёт'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Запланировано'),
        ('in_progress', 'Выполняется'),
        ('completed', 'Выполнено'),
        ('failed', 'Ошибка'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    task_type = models.CharField(max_length=20, choices=TASK_TYPES)
    input_data = models.JSONField()  # Хранение входных данных задачи
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    result = models.JSONField(null=True, blank=True)  # Хранение результата выполнения
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Задача {self.task_type} от {self.user.username}"
