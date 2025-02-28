# Используем официальный образ Python
FROM python:3.12.5-alpine

# Устанавливаем рабочую директорию в контейнере
WORKDIR /app

# Копируем файлы проекта в контейнер
COPY . /app

# Копируем файл зависимостей и устанавливаем их
COPY requirements.txt .

# Устанавливаем зависимости
RUN pip install --no-cache-dir -r requirements.txt

# Экспонируем порт для FastAPI
EXPOSE 8000
