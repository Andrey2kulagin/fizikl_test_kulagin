import pytest
from rest_framework.test import APIClient
from rest_framework import status
from django.urls import reverse
from django.contrib.auth import get_user_model
from tasks.models import Task
User = get_user_model()


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def create_user():
    def _create_user(username, password):
        email = username+'@fizikl.org'
        user = User.objects.create_user(
            username=username, password=password, email=email)
        return user
    return _create_user


@pytest.fixture
def get_token(api_client, create_user):
    def _get_token(username, password):
        create_user(username, password)
        response = api_client.post(reverse('token_obtain_pair'), {
            'username': username,
            'password': password,
        })
        return response.data['access']
    return _get_token


@pytest.mark.django_db
def test_register_user(api_client):
    response = api_client.post(reverse('register'), {
        'username': 'testuser',
        'password': 'Password123FIZIKL',
        'email': 'testuser@fizikl.org',
        'password_confirm': 'Password123FIZIKL'

    })
    assert response.status_code == status.HTTP_201_CREATED


@pytest.mark.django_db
def test_register_user_already_exist(api_client):
    """
    Уже есть пользователь с таким логином или почтой
    """
    response = api_client.post(reverse('register'), {
        'username': 'testuser',
        'password': 'Password123FIZIKL',
        'email': 'testuser@fizikl.org',
        'password_confirm': 'Password123FIZIKL'

    })
    response = api_client.post(reverse('register'), {
        'username': 'testuser',
        'password': 'Password123FIZIKL',
        'email': 'testuser@fizikl.org',
        'password_confirm': 'Password123FIZIKL'

    })
    assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
def test_create_task(api_client, get_token):
    token = get_token('testuser', 'password123')
    api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')

    response = api_client.post(reverse('task-list'), {
        'task_type': 'sum',
        'input_data': {'a': 1, 'b': 2}
    }, format='json')

    assert response.status_code == status.HTTP_201_CREATED
    assert response.data['task_type'] == 'sum'


@pytest.mark.django_db
def test_create_task_from_list(api_client, get_token):
    token = get_token('testuser', 'password123')
    api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')

    response = api_client.post(reverse('task-list'), {
        'task_type': 'sum',
        'input_data': [1, 2, 3]
    }, format='json')

    assert response.status_code == status.HTTP_201_CREATED
    assert response.data['task_type'] == 'sum'


@pytest.mark.django_db
def test_get_token_by_email(api_client, create_user, get_token):
    username = 'test_user'
    password = 'Password123FIZIKL'
    create_user(username, password)
    response = api_client.post(reverse('token_obtain_pair'), {
        'username': username,
        'password': password,
    })
    token = response.data['access']
    api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
    response = api_client.post(reverse('task-list'), {
        'task_type': 'sum',
        'input_data': [1, 2, 3]
    }, format='json')
    assert response.status_code == status.HTTP_201_CREATED
    assert response.data['task_type'] == 'sum'


@pytest.mark.django_db
def test_task_list(api_client, get_token):
    token = get_token('testuser', 'password123')
    api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
    api_client.post(reverse('task-list'), {
        'task_type': 'countdown',
        'input_data': {'seconds': 5}
    }, format='json')
    response = api_client.get(reverse('task-list'))
    assert response.status_code == status.HTTP_200_OK
    assert len(response.data['results']) == 1


@pytest.mark.django_db
def test_task_detail(api_client, get_token):
    token = get_token('testuser', 'password123')
    api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
    task_response = api_client.post(reverse('task-list'), {
        'task_type': 'sum',
        'input_data': {'a': 1, 'b': 2}
    }, format='json')
    task_id = task_response.data['id']
    response = api_client.get(reverse('task-detail', args=[task_id]))
    assert response.status_code == status.HTTP_200_OK
    assert response.data['task_type'] == 'sum'

@pytest.mark.django_db
def test_task_create_not_auth(api_client, get_token):
    api_client.credentials(HTTP_AUTHORIZATION=f'Bearer 1234')
    task_response = api_client.post(reverse('task-list'), {
        'task_type': 'sum',
        'input_data': {'a': 1, 'b': 2}
    }, format='json')
    assert task_response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
def test_task_pending_tasks(api_client, get_token):
    token = get_token('testuser', 'password123')
    api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
    task_response = api_client.post(reverse('task-list'), {
        'task_type': 'countdown',
        'input_data': {"time": 123}
    }, format='json')
    task_response = api_client.post(reverse('task-list'), {
        'task_type': 'countdown',
        'input_data': {"time": 123}
    }, format='json')
    task_id_2 = task_response.data['id']
    response = api_client.get(reverse('task-detail', args=[task_id_2]))

    assert response.status_code == status.HTTP_200_OK
    assert response.data['task_type'] == 'countdown'
    assert response.data['status'] == 'pending'


@pytest.mark.django_db
def test_task_limit(api_client, get_token):
    token = get_token('testuser', 'password123')
    api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
    for _ in range(5):
        response = api_client.post(reverse('task-list'), {
            'task_type': 'sum',
            'input_data': {'a': 1, 'b': 2}
        }, format='json')
        assert response.status_code == status.HTTP_201_CREATED
    response = api_client.post(reverse('task-list'), {
        'task_type': 'sum',
        'input_data': {'a': 1, 'b': 2}
    }, format='json')
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert 'non_field_errors' in response.data


@pytest.mark.django_db
def test_task_status_and_result(api_client, get_token):
    token = get_token('testuser', 'password123')
    api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
    task_response = api_client.post(reverse('task-list'), {
        'task_type': 'sum',
        'input_data': {'a': 5, 'b': 3}
    }, format='json')
    task_id = task_response.data['id']
    response = api_client.get(reverse('task-detail', args=[task_id]))
    assert response.status_code == status.HTTP_200_OK
    assert response.data['status'] in ['pending', 'in_progress', 'completed']
    if response.data['status'] == 'completed':
        assert response.data['result'] == 8


@pytest.mark.django_db
def test_task_list_many_users(api_client, get_token):
    token = get_token('testuser', 'password123')
    api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
    for _ in range(3):
        response = api_client.post(reverse('task-list'), {
            'task_type': 'sum',
            'input_data': {'a': 1, 'b': 2}
        }, format='json')

    token = get_token('testuser1', 'password123')
    api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
    for _ in range(3):
        response = api_client.post(reverse('task-list'), {
            'task_type': 'sum',
            'input_data': {'a': 1, 'b': 2}
        }, format='json')
    response = api_client.get(reverse('task-list'))
    print(response.data)
    assert 3 == len(response.data['results'])


@pytest.mark.django_db
def test_task_get(api_client, get_token):
    token = get_token('testuser', 'password123')
    api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
    response = api_client.post(reverse('task-list'), {
        'task_type': 'sum',
        'input_data': {'a': 1, 'b': 2}
    }, format='json')
    first_user_task_id = response.data['id']
    token = get_token('testuser1', 'password123')
    api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
    response = api_client.post(reverse('task-list'), {
        'task_type': 'sum',
        'input_data': {'a': 1, 'b': 2}
    }, format='json')
    response = api_client.get(
        reverse('task-detail', args=[first_user_task_id]))

    print(response.data)
    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db
def test_task_get(api_client, get_token):
    token = get_token('testuser', 'password123')
    api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
    response = api_client.post(reverse('task-list'), {
        'task_type': 'sum',
        'input_data': {'a': 1, 'b': 2}
    }, format='json')
    token = get_token('testuser1', 'password123')
    api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
    response = api_client.post(reverse('task-list'), {
        'task_type': 'sum',
        'input_data': {'a': 1, 'b': 2}
    }, format='json')
    second_user_task_id = response.data['id']
    response = api_client.get(
        reverse('task-detail', args=[second_user_task_id]))
    print(response.data)
    assert response.status_code == status.HTTP_200_OK


@pytest.mark.django_db
def test_filter_tasks_by_status(api_client, get_token):
    token = get_token('testuser', 'password123')
    api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
    for i in range(3):
        response = api_client.post(reverse('task-list'), {
            'task_type': 'sum',
            'input_data': [i, i+1]
        }, format='json')
        assert response.status_code == status.HTTP_201_CREATED
    response = api_client.get(reverse('task-list') + '?status=pending')
    assert response.status_code == status.HTTP_200_OK
    assert len(response.data['results']) == 3  # Все задачи в статусе 'pending'
    task_id = response.data['results'][0]['id']
    Task.objects.filter(id=task_id).update(status='completed')
    response = api_client.get(reverse('task-list') + '?status=completed')
    assert response.status_code == status.HTTP_200_OK
    assert len(response.data['results']) == 1
    assert response.data['results'][0]['id'] == task_id


@pytest.mark.django_db
def test_sort_tasks_by_id(api_client, get_token):
    token = get_token('testuser', 'password123')
    api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
    ids = []
    for i in range(3):
        response = api_client.post(reverse('task-list'), {
            'task_type': 'sum',
            'input_data': [i, i+1]
        }, format='json')
        assert response.status_code == status.HTTP_201_CREATED
        ids.append(response.data['id'])

    # Проверка сортировки по возрастанию ID
    response = api_client.get(reverse('task-list') + '?ordering=id')
    assert response.status_code == status.HTTP_200_OK
    returned_ids = [task['id'] for task in response.data['results']]
    assert returned_ids == sorted(ids)

    # Проверка сортировки по убыванию ID
    response = api_client.get(reverse('task-list') + '?ordering=-id')
    assert response.status_code == status.HTTP_200_OK
    returned_ids = [task['id'] for task in response.data['results']]
    assert returned_ids == sorted(ids, reverse=True)


@pytest.mark.django_db
def test_filter_and_sort_tasks(api_client, get_token):
    token = get_token('testuser', 'password123')
    api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')

    # Создание задач
    ids = []
    for i in range(5):
        response = api_client.post(reverse('task-list'), {
            'task_type': 'sum',
            'input_data': [i, i+1]
        }, format='json')
        assert response.status_code == status.HTTP_201_CREATED
        ids.append(response.data['id'])

    # Изменение статусов
    Task.objects.filter(id=ids[0]).update(status='completed')
    Task.objects.filter(id=ids[1]).update(status='completed')

    # Фильтрация по статусу и сортировка по ID
    response = api_client.get(
        reverse('task-list') + '?status=completed&ordering=-id')
    assert response.status_code == status.HTTP_200_OK

    returned_ids = [task['id'] for task in response.data['results']]
    # Только завершённые задачи, отсортированные по убыванию ID
    assert returned_ids == sorted(ids[:2], reverse=True)
