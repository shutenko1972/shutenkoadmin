FROM python:3.11-slim

WORKDIR /app

# Копируем файлы приложения
COPY . .

# Устанавливаем зависимости
RUN pip install --no-cache-dir flask flask-sqlalchemy flasgger

# Создаем папку для базы данных
RUN mkdir -p instance

# Открываем порт
EXPOSE 5000

# Запускаем приложение
CMD ["python", "app.py"]