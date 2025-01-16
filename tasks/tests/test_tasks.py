import pytest
from rest_framework.test import APIClient
from rest_framework import status
from django.urls import reverse
from django.contrib.auth import get_user_model
User = get_user_model()

@pytest.fixture
def api_client():
    return APIClient()

@pytest.fixture
def create_user():
    def _create_user(username, password):
        email = username+'@fizikl.org'
        user = User.objects.create_user(username=username, password=password, email=email)
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
        'password_confirm':'Password123FIZIKL'
        
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
        'password_confirm':'Password123FIZIKL'
        
    })
    response = api_client.post(reverse('register'), {
        'username': 'testuser',
        'password': 'Password123FIZIKL',
        'email': 'testuser@fizikl.org',
        'password_confirm':'Password123FIZIKL'
        
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
        'input_data': [1,2,3]
    }, format='json')

    assert response.status_code == status.HTTP_201_CREATED
    assert response.data['task_type'] == 'sum'
    
@pytest.mark.django_db
def test_get_token_by_email(api_client, create_user, get_token):
    username = 'test_user'
    password = 'Password123FIZIKL'
    
    # Используем фикстуру для создания пользователя
    create_user(username, password)
    
    # Получаем токен
    response = api_client.post(reverse('token_obtain_pair'), {
        'username': username,
        'password': password,
    })
    token = response.data['access']
    api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')

    # Создаём задачу
    response = api_client.post(reverse('task-list'), {
        'task_type': 'sum',
        'input_data': [1, 2, 3]
    }, format='json')

    # Проверяем статус и ответ
    assert response.status_code == status.HTTP_201_CREATED
    assert response.data['task_type'] == 'sum'

@pytest.mark.django_db
def test_task_list(api_client, get_token):
    token = get_token('testuser', 'password123')
    api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')

    # Create a task
    api_client.post(reverse('task-list'), {
        'task_type': 'countdown',
        'input_data': {'seconds': 5}
    }, format='json')

    # Get task list
    response = api_client.get(reverse('task-list'))

    assert response.status_code == status.HTTP_200_OK
    assert len(response.data) == 1
    


@pytest.mark.django_db
def test_task_detail(api_client, get_token):
    token = get_token('testuser', 'password123')
    api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')

    # Create a task
    task_response = api_client.post(reverse('task-list'), {
        'task_type': 'sum',
        'input_data': {'a': 1, 'b': 2}
    }, format='json')

    task_id = task_response.data['id']

    # Get task detail
    response = api_client.get(reverse('task-detail', args=[task_id]))

    assert response.status_code == status.HTTP_200_OK
    assert response.data['task_type'] == 'sum'


@pytest.mark.django_db
def test_task_pending_tasks(api_client, get_token):
    token = get_token('testuser', 'password123')
    api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')

    # Create a task
    task_response = api_client.post(reverse('task-list'), {
        'task_type': 'countdown',
        'input_data': {"time":123}
    }, format='json')

    task_id_1 = task_response.data['id']
    
    task_response = api_client.post(reverse('task-list'), {
        'task_type': 'countdown',
        'input_data': {"time":123}
    }, format='json')

    task_id_2 = task_response.data['id']

    # Get task detail
    response = api_client.get(reverse('task-detail', args=[task_id_2]))

    assert response.status_code == status.HTTP_200_OK
    assert response.data['task_type'] == 'countdown'
    assert response.data['status'] == 'pending'
    
    

@pytest.mark.django_db
def test_task_limit(api_client, get_token):
    token = get_token('testuser', 'password123')
    api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')

    # Create 5 tasks
    for _ in range(5):
        response = api_client.post(reverse('task-list'), {
            'task_type': 'sum',
            'input_data': {'a': 1, 'b': 2}
        }, format='json')
        assert response.status_code == status.HTTP_201_CREATED

    # Attempt to create a 6th task
    response = api_client.post(reverse('task-list'), {
        'task_type': 'sum',
        'input_data': {'a': 1, 'b': 2}
    }, format='json')

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert 'non_field_errors' in response.data
"""
@pytest.mark.django_db
def test_task_status_and_result(api_client, get_token):
    token = get_token('testuser', 'password123')
    api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')

    # Create a task
    task_response = api_client.post(reverse('task-list'), {
        'task_type': 'sum',
        'input_data': {'a': 5, 'b': 3}
    }, format='json')

    task_id = task_response.data['id']

    # Poll for status
    response = api_client.get(reverse('task-detail', args=[task_id]))
    assert response.status_code == status.HTTP_200_OK
    assert response.data['status'] in ['scheduled', 'in_progress', 'completed']

    # Check result (assuming task completed)
    if response.data['status'] == 'completed':
        assert response.data['result'] == 8
        """