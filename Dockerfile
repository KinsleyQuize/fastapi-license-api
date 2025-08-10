# Используем официальный Python образ
FROM python:3.11-slim

# Устанавливаем рабочую директорию внутри контейнера
WORKDIR /app

# Копируем файлы зависимостей и устанавливаем их
COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

# Копируем все файлы проекта в контейнер
COPY . .

# Пробрасываем порт, на котором будет работать uvicorn
EXPOSE 8000

# Команда запуска uvicorn с нужными параметрами
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
