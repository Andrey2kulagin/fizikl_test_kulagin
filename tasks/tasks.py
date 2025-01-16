from celery import shared_task
from .models import Task
from celery.signals import task_prerun, task_postrun
import time
import random


@shared_task
def sum_task(task_id):
    task = Task.objects.get(id=task_id)
    if random.random() < 0.2:  # 20% вероятность ошибки
        raise ValueError("Случайная ошибка в sum_task")
    result = sum(task.input_data)
    task.save()

    return result


@shared_task
def countdown_task(task_id):
    task = Task.objects.get(id=task_id)
    countdown_time = task.input_data.get('time', 0)
    if random.random() < 0.2:  # 20% вероятность ошибки
        raise ValueError("Случайная ошибка в sum_task")
    time.sleep(countdown_time)
    return task.result


@task_prerun.connect
def update_task_status_to_in_progress(sender, task_id, task, args, kwargs, **_):
    """
    Обновляет статус задачи на 'in_progress' перед началом выполнения.
    """
    if sender.name in ['tasks.tasks.sum_task', 'tasks.tasks.countdown_task']:
        # ID передается первым аргументом
        task_instance = Task.objects.get(id=args[0])
        task_instance.status = 'in_progress'
        task_instance.save()


@task_postrun.connect
def update_task_status_to_completed(sender, task_id, task, args, kwargs, retval, state, **_):
    """
    Обновляет статус задачи на 'completed' после завершения выполнения.
    """
    if sender.name in ['tasks.tasks.sum_task', 'tasks.tasks.countdown_task']:
        task_instance = Task.objects.get(id=args[0])
        if state == 'SUCCESS':
            task_instance.status = 'completed'
            task_instance.result = retval  # Результат задачи сохраняется
        elif state == 'FAILURE':
            task_instance.status = 'failed'
        task_instance.save()
