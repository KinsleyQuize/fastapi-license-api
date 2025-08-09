# Используем официальный Python образ
FROM python:3.11-slim

# Устанавливаем рабочую директорию в контейнере
WORKDIR /app

# Копируем файлы requirements.txt и main.py в контейнер
COPY requirements.txt .
COPY main.py .

# Устанавливаем зависимости
RUN pip install --no-cache-dir -r requirements.txt

# Устанавливаем переменные окружения (можно задать в Render UI)
ENV FLASK_APP=main.py
ENV FLASK_RUN_HOST=0.0.0.0

# Открываем порт (Render читает этот порт из переменной PORT)
EXPOSE 5000

# Команда запуска Flask-сервера
CMD ["flask", "run", "--host=0.0.0.0", "--port=5000"]
