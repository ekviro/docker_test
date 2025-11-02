import requests
import os


def test_server_root():
    """Тест главной страницы сервера"""
    # Автоматически определяем URL: в Docker или локально (если в композе есть API_URL, то берем ее, иначе - локалхост)
    base_url = os.getenv("API_URL", "http://localhost:8000")

    response = requests.get(f"{base_url}/")
    assert response.status_code == 200
    assert response.json()["message"] == "Сервер работает!"
    print("✅ Тест главной страницы пройден!")


def test_get_users():
    """Тест получения пользователей"""
    base_url = os.getenv("API_URL", "http://localhost:8000")

    response = requests.get(f"{base_url}/users")
    assert response.status_code == 200
    users = response.json()
    assert isinstance(users, list)
    assert len(users) >= 2  # Должны быть тестовые данные из БД
    print("✅ Тест получения пользователей пройден!")
