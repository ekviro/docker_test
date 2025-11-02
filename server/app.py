from fastapi import FastAPI
import psycopg2
from psycopg2.extras import RealDictCursor
import os

# Создаем приложение FastAPI
app = FastAPI(title="User API")

def get_db_connection():
    """Функция для подключения к базе данных"""
    # Автоматически определяем хост: в Docker - "postgres", локально - "localhost"
    db_host = os.getenv("DB_HOST", "localhost")
    return psycopg2.connect(
        host=db_host,  # 👈 теперь работает в обоих режимах
        database="mydatabase", # название базы данных
        user="myuser",        # пользователь
        password="mypassword", # пароль
        port="5432"          # порт PostgreSQL
    )

@app.get("/")
def read_root():
    """Простой эндпоинт для проверки работы сервера"""
    return {"message": "Сервер работает!"}

@app.get("/users")
def get_users():
    """Эндпоинт для получения списка всех пользователей"""
    conn = get_db_connection()
    # RealDictCursor возвращает результаты как словари (удобнее чем кортежи)
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute("SELECT * FROM users")
    users = cur.fetchall()
    cur.close()
    conn.close()
    return users