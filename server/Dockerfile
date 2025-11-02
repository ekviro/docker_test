# Используем официальный образ Python
FROM python:3.11

# Устанавливаем рабочую директорию внутри контейнера
WORKDIR /app

# Копируем и устанавливаем ТОЛЬКО серверные зависимости
COPY requirements-server.txt .
RUN pip install -r requirements-server.txt

# Копируем код сервера в контейнер
COPY server/ .

# Команда для запуска FastAPI сервера
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]