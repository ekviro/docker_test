# Используем официальный образ Python
FROM python:3.11

# Устанавливаем рабочую директорию внутри контейнера
WORKDIR /app

# Копируем и устанавливаем ТОЛЬКО тестовые зависимости
COPY requirements-tests.txt .
RUN pip install -r requirements-tests.txt

# Копируем ВСЕ и запускаем тесты из папки tests (иначе не запускалось)
COPY . .

# Ждем 5 секунд чтобы сервер успел запуститься, затем запускаем тесты
CMD ["sh", "-c", "sleep 5 && pytest tests/ -v"]