from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import psycopg2
from psycopg2.extras import RealDictCursor
import os
from typing import List, Optional
from datetime import datetime

# Создаем приложение FastAPI
app = FastAPI(title="User API", version="1.0.0")


# Модели данных для валидации
class UserCreate(BaseModel):
    """Модель для создания пользователя"""
    username: str
    email: str
    full_name: str

class UserResponse(BaseModel):
    """Модель для ответа с данными пользователя"""
    id: int
    username: str
    email: str
    full_name: str
    created_at: datetime

class AddressCreate(BaseModel):
    """Модель для создания адреса"""
    user_id: int
    country: str
    city: str
    street: str
    house_number: Optional[str] = None

class AddressResponse(BaseModel):
    """Модель для ответа с данными адреса"""
    id: int
    user_id: int
    country: str
    city: str
    street: str
    house_number: Optional[str]
    created_at: datetime


def get_db_connection():
    """Функция для подключения к базе данных"""
    # Автоматически определяем хост: если в композе нет DB_HOST, то - "localhost"
    db_host = os.getenv("DB_HOST", "localhost")

    return psycopg2.connect(
        host=db_host,  # Имя сервиса БД в Docker или localhost при локальном запуске
        database="mydatabase",  # Название базы данных
        user="myuser",  # Пользователь БД
        password="mypassword",  # Пароль БД
        port="5432"  # Порт PostgreSQL
    )


# GET эндпоинты
@app.get("/", tags=["Health"])
def read_root():
    """Простой эндпоинт для проверки работы сервера"""
    return {"message": "Сервер работает!", "status": "ok"}


@app.get("/users", response_model=List[UserResponse], tags=["Users"])
def get_users():
    """Эндпоинт для получения списка всех пользователей"""
    conn = get_db_connection()
    # RealDictCursor возвращает результаты как словари (удобнее чем кортежи)
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute("SELECT id, username, email, full_name, created_at FROM users ORDER BY id")
    users = cur.fetchall()
    cur.close()
    conn.close()
    return users


@app.get("/users/{user_id}", response_model=UserResponse, tags=["Users"])
def get_user(user_id: int):
    """Эндпоинт для получения конкретного пользователя по ID"""
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)

    cur.execute(
        "SELECT id, username, email, full_name, created_at FROM users WHERE id = %s",
        (user_id,)
    )
    user = cur.fetchone()
    cur.close()
    conn.close()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@app.get("/users/{user_id}/addresses", response_model=List[AddressResponse], tags=["Addresses"])
def get_user_addresses(user_id: int):
    """Эндпоинт для получения всех адресов пользователя"""
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)

    cur.execute(
        "SELECT id, user_id, country, city, street, house_number, created_at FROM addresses WHERE user_id = %s",
        (user_id,)
    )
    addresses = cur.fetchall()
    cur.close()
    conn.close()

    return addresses


@app.get("/addresses", response_model=List[AddressResponse], tags=["Addresses"])
def get_all_addresses():
    """Эндпоинт для получения всех адресов"""
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)

    cur.execute("SELECT id, user_id, country, city, street, house_number, created_at FROM addresses")
    addresses = cur.fetchall()
    cur.close()
    conn.close()

    return addresses


# POST эндпоинты
@app.post("/users", response_model=UserResponse, tags=["Users"], status_code=201)
def create_user(user: UserCreate):
    """Эндпоинт для создания нового пользователя"""
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)

    try:
        # Вставляем нового пользователя и возвращаем созданную запись
        cur.execute(
            """INSERT INTO users (username, email, full_name) 
               VALUES (%s, %s, %s) 
               RETURNING id, username, email, full_name, created_at""",
            (user.username, user.email, user.full_name)
        )
        new_user = cur.fetchone()
        conn.commit()
        return new_user
    except psycopg2.IntegrityError as e:
        conn.rollback()
        # Проверяем какое именно ограничение нарушено
        if "username" in str(e):
            raise HTTPException(status_code=400, detail="Username already exists")
        elif "email" in str(e):
            raise HTTPException(status_code=400, detail="Email already exists")
        else:
            raise HTTPException(status_code=400, detail="User creation failed")
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    finally:
        cur.close()
        conn.close()


@app.post("/addresses", response_model=AddressResponse, tags=["Addresses"], status_code=201)
def create_address(address: AddressCreate):
    """Эндпоинт для создания нового адреса"""
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)

    try:
        # Сначала проверяем существует ли пользователь
        cur.execute("SELECT id FROM users WHERE id = %s", (address.user_id,))
        if not cur.fetchone():
            raise HTTPException(status_code=404, detail="User not found")

        # Вставляем новый адрес и возвращаем созданную запись
        cur.execute(
            """INSERT INTO addresses (user_id, country, city, street, house_number) 
               VALUES (%s, %s, %s, %s, %s) 
               RETURNING id, user_id, country, city, street, house_number, created_at""",
            (address.user_id, address.country, address.city, address.street, address.house_number)
        )
        new_address = cur.fetchone()
        conn.commit()
        return new_address
    except HTTPException:
        conn.rollback()
        raise  # Пробрасываем HTTPException дальше
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    finally:
        cur.close()
        conn.close()


# PUT эндпоинты
@app.put("/users/{user_id}", response_model=UserResponse, tags=["Users"])
def update_user(user_id: int, user: UserCreate):
    """Эндпоинт для обновления пользователя"""
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)

    try:
        cur.execute(
            """UPDATE users 
               SET username = %s, email = %s, full_name = %s 
               WHERE id = %s 
               RETURNING id, username, email, full_name, created_at""",
            (user.username, user.email, user.full_name, user_id)
        )
        updated_user = cur.fetchone()
        conn.commit()

        if not updated_user:
            raise HTTPException(status_code=404, detail="User not found")
        return updated_user
    except psycopg2.IntegrityError as e:
        conn.rollback()
        if "username" in str(e):
            raise HTTPException(status_code=400, detail="Username already exists")
        elif "email" in str(e):
            raise HTTPException(status_code=400, detail="Email already exists")
        else:
            raise HTTPException(status_code=400, detail="User update failed")
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    finally:
        cur.close()
        conn.close()


# DELETE эндпоинты
@app.delete("/users/{user_id}", tags=["Users"])
def delete_user(user_id: int):
    """Эндпоинт для удаления пользователя (и его адресов через CASCADE)"""
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)

    try:
        # Сначала проверяем существует ли пользователь
        cur.execute("SELECT id FROM users WHERE id = %s", (user_id,))
        if not cur.fetchone():
            raise HTTPException(status_code=404, detail="User not found")

        # Удаляем пользователя (адреса удалятся автоматически благодаря CASCADE)
        cur.execute("DELETE FROM users WHERE id = %s", (user_id,))
        conn.commit()

        return {"message": f"User {user_id} deleted successfully"}
    except HTTPException:
        conn.rollback()
        raise
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    finally:
        cur.close()
        conn.close()


@app.delete("/addresses/{address_id}", tags=["Addresses"])
def delete_address(address_id: int):
    """Эндпоинт для удаления адреса"""
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)

    try:
        cur.execute("DELETE FROM addresses WHERE id = %s", (address_id,))
        conn.commit()

        if cur.rowcount == 0:
            raise HTTPException(status_code=404, detail="Address not found")

        return {"message": f"Address {address_id} deleted successfully"}
    except HTTPException:
        conn.rollback()
        raise
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    finally:
        cur.close()
        conn.close()


# GET эндпоинты для поиска
@app.get("/users/search/", response_model=List[UserResponse], tags=["Search"])
def search_users(
        username: Optional[str] = None,
        email: Optional[str] = None,
        full_name: Optional[str] = None
):
    """
    Эндпоинт для поиска пользователей по различным критериям.
    Можно искать по username, email или full_name (или комбинации).

    Примеры использования:
    - /users/search/?username=ivanov
    - /users/search/?email=example.com
    - /users/search/?full_name=Иван
    - /users/search/?username=ivanov&email=example.com
    """
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)

    try:
        # Базовый SQL запрос
        sql = "SELECT id, username, email, full_name, created_at FROM users WHERE 1=1"
        params = []

        # Динамически добавляем условия поиска
        if username:
            sql += " AND username ILIKE %s"
            params.append(f"%{username}%")

        if email:
            sql += " AND email ILIKE %s"
            params.append(f"%{email}%")

        if full_name:
            sql += " AND full_name ILIKE %s"
            params.append(f"%{full_name}%")

        # Добавляем сортировку по ID
        sql += " ORDER BY id"

        # Выполняем запрос
        cur.execute(sql, params)
        users = cur.fetchall()

        return users

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search error: {str(e)}")
    finally:
        cur.close()
        conn.close()


@app.get("/users/search/{user_id_or_username}", response_model=UserResponse, tags=["Search"])
def get_user_by_id_or_username(user_id_or_username: str):
    """
    Эндпоинт для поиска пользователя по ID или username.
    Автоматически определяет - передан ID или username.

    Примеры использования:
    - /users/search/1          (поиск по ID)
    - /users/search/ivanov     (поиск по username)
    """
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)

    try:
        # Пытаемся преобразовать в число - если получится, ищем по ID
        if user_id_or_username.isdigit():
            user_id = int(user_id_or_username)
            cur.execute(
                "SELECT id, username, email, full_name, created_at FROM users WHERE id = %s",
                (user_id,)
            )
        else:
            # Иначе ищем по username
            cur.execute(
                "SELECT id, username, email, full_name, created_at FROM users WHERE username = %s",
                (user_id_or_username,)
            )

        user = cur.fetchone()

        if not user:
            raise HTTPException(
                status_code=404,
                detail=f"User with ID or username '{user_id_or_username}' not found"
            )
        return user

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search error: {str(e)}")
    finally:
        cur.close()
        conn.close()


@app.get("/users/{user_id}/exists", tags=["Search"])
def check_user_exists(user_id: int):
    """
    Эндпоинт для проверки существования пользователя по ID.
    Возвращает простой ответ с булевым значением.

    Пример: /users/1/exists
    """
    conn = get_db_connection()
    cur = conn.cursor()

    try:
        cur.execute("SELECT 1 FROM users WHERE id = %s", (user_id,))
        exists = cur.fetchone() is not None

        return {"exists": exists, "user_id": user_id}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Check error: {str(e)}")
    finally:
        cur.close()
        conn.close()


@app.get("/users/email/{email}/exists", tags=["Search"])
def check_email_exists(email: str):
    """
    Эндпоинт для проверки существования email.
    Полезно для проверки при регистрации новых пользователей.

    Пример: /users/email/ivanov@example.com/exists
    """
    conn = get_db_connection()
    cur = conn.cursor()

    try:
        cur.execute("SELECT 1 FROM users WHERE email = %s", (email,))
        exists = cur.fetchone() is not None

        return {"exists": exists, "email": email}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Check error: {str(e)}")
    finally:
        cur.close()
        conn.close()
