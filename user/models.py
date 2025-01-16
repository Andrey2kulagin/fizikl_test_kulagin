from django.contrib.auth.models import AbstractUser

from django.db import models

class CustomUser(AbstractUser):
    email = models.EmailField(unique=True)
    
    # Переопределяем метод для аутентификации по email или username
    def authenticate(self, username=None, email=None, password=None):
        if username:
            return self.objects.get(username=username).check_password(password)
        if email:
            return self.objects.get(email=email).check_password(password)
        return None
