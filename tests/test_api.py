import pytest
import requests
import os


class TestAPI:
    """Тесты для API сервера"""

    @pytest.fixture
    def base_url(self):
        """Фикстура для базового URL"""
        return os.getenv("API_URL", "http://localhost:8000")

    def test_server_root(self, base_url):
        """Тест главной страницы сервера"""
        response = requests.get(f"{base_url}/")
        assert response.status_code == 200
        assert response.json()["message"] == "Сервер работает!"

    def test_get_users(self, base_url):
        """Тест получения пользователей"""
        response = requests.get(f"{base_url}/users")
        assert response.status_code == 200
        users = response.json()
        assert isinstance(users, list)
        assert len(users) >= 2

    @pytest.mark.parametrize("user_id", [1, 2])
    def test_get_user_by_id(self, base_url, user_id):
        """Тест получения пользователя по разным ID"""
        response = requests.get(f"{base_url}/users/{user_id}")
        assert response.status_code == 200
        user = response.json()
        assert user["id"] == user_id

    def test_get_nonexistent_user(self, base_url):
        """Тест получения несуществующего пользователя"""
        response = requests.get(f"{base_url}/users/999")
        assert response.status_code == 404


# Или с фикстурами на уровне модуля
@pytest.fixture(scope="module")
def api_client():
    """Фикстура для API клиента"""
    base_url = os.getenv("API_URL", "http://localhost:8000")

    class APIClient:
        def __init__(self, base_url):
            self.base_url = base_url

        def get(self, endpoint):
            return requests.get(f"{self.base_url}{endpoint}")

        def post(self, endpoint, json_data):
            return requests.post(f"{self.base_url}{endpoint}", json=json_data)

    return APIClient(base_url)


def test_with_client_fixture(api_client):
    """Тест с использованием фикстуры клиента"""
    response = api_client.get("/users")
    assert response.status_code == 200
