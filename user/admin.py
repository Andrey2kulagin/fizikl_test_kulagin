from django.contrib import admin
from .models import CustomUser
from .forms import EmailOrUsernameLoginForm
from django.contrib.auth.models import Group, Permission

# Регистрируем стандартные модели в админке

class CustomAdminSite(admin.AdminSite):
    login_form = EmailOrUsernameLoginForm  # Если хотите кастомизировать форму

admin_site = CustomAdminSite()

class CustomUserAdmin(admin.ModelAdmin):
    pass

admin_site.register(CustomUser, CustomUserAdmin)  # Регистрируем пользователя в кастомном админ-сайте
admin_site.register(Group)
admin_site.register(Permission)