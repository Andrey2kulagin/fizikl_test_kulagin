from django.contrib import admin
from .models import CustomUser
from .forms import EmailOrUsernameLoginForm
from django.contrib.auth.models import Group, Permission

admin.site.login_form = EmailOrUsernameLoginForm

admin.site.register(CustomUser)
