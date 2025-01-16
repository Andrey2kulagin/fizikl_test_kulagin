from django.contrib.auth.backends import ModelBackend
from user.models import CustomUser


class EmailOrUsernameBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        user = None
        # Пытаемся найти пользователя по имени
        if username:
            user = CustomUser.objects.filter(username=username).first()
        # Пытаемся найти пользователя по email
        if not user and kwargs.get('email'):
            user = CustomUser.objects.filter(email=kwargs.get('email')).first()

        if user and user.check_password(password):
            return user
        return None
