from django import forms
from django.contrib.auth.forms import AuthenticationForm
from .models import CustomUser

# форма для входа в админке по email или username
class EmailOrUsernameLoginForm(AuthenticationForm):
    username = forms.CharField(label='Логин или Email')

    def clean_username(self):
        username_or_email = self.cleaned_data.get('username')

        # Пытаемся найти пользователя по email
        try:
            user = CustomUser.objects.get(email=username_or_email)
            return user.username  # Возвращаем username, чтобы стандартная аутентификация сработала
        except CustomUser.DoesNotExist:
            # Если по email не нашли, проверяем по username
            try:
                user = CustomUser.objects.get(username=username_or_email)
                return user.username  # Возвращаем username
            except CustomUser.DoesNotExist:
                raise forms.ValidationError(
                    "Пользователь с таким email или логином не существует.")
