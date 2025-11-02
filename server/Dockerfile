# Используем официальный образ Python
FROM python:3.11

# Устанавливаем рабочую директорию внутри контейнера
WORKDIR /app

# Копируем файл с зависимостями
COPY requirements.txt .

# Устанавливаем зависимости
RUN pip install -r requirements.txt

# Копируем код сервера в контейнер
COPY server/ .

# Команда для запуска сервера
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]