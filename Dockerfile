# Используем официальный Python образ
FROM python:3.11-slim

# Устанавливаем рабочую директорию
WORKDIR /app

# Копируем файл с зависимостями
COPY requirements.txt .

# Устанавливаем зависимости
RUN pip install --no-cache-dir -r requirements.txt

# Копируем весь проект
COPY . .

# Создаем пользователя для безопасности
RUN useradd -m -u 1000 flaskuser && \
    chown -R flaskuser:flaskuser /app

# Переключаемся на непривилегированного пользователя
USER flaskuser

# Открываем порт
EXPOSE 5000

# Переменные окружения для Flask
ENV FLASK_APP=app.py
ENV FLASK_ENV=production
ENV PYTHONUNBUFFERED=1

# Команда запуска
ENTRYPOINT ["python", "app.py"]