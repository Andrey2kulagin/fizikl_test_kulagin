# Используем официальный образ Python
FROM python:3.10-slim

# Устанавливаем рабочую директорию
WORKDIR /app

# Копируем файлы зависимостей
COPY requirements.txt /app/

# Устанавливаем зависимости
RUN pip install --no-cache-dir -r requirements.txt
# Копируем все файлы проекта в контейнер
COPY . /app/

# Открываем порт для Django
EXPOSE 8000

# Команда для запуска сервера Django
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "core.wsgi:application"]
