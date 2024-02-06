from httpx import Response, AsyncClient

from app.config import settings


class TestAuthUser:
    """Класс для работы с пользователем"""

    async def test_register_client(self, async_client: AsyncClient) -> None:
        """Регистрация пользователя"""
        response: Response = await async_client.post(url="/api/v1/auth/register", json={
            "username": "User",
            "password": "string1fadH!",
            "email": "user@example.com"
        })
        assert response.status_code == 201, f"Ошибка при создании пользователя: {response.text}"
        assert len(response.json()) == 3
        assert response.json()["id"] == 1
        assert response.json()["username"] == "User"
        assert response.json()["email"] == "user@example.com"

    async def test_login_client(self, async_client: AsyncClient) -> None:
        """Аутентификация пользователя"""
        response_login: Response = await async_client.post(url="/api/v1/auth/login", data={
            "email": "user@example.com",
            "password": "string1fadH!",
        })
        cookie_key = settings.session_cookie.COOKIE_SESSION_KEY
        assert response_login.status_code == 200, f"Ошибка авторизации: {response_login.text}"
        assert cookie_key in response_login.cookies, f"не существует ключа {cookie_key} в куках"
        assert "access_token" in response_login.cookies.get(cookie_key), "access_token не найден в куках"
        assert "refresh_token" in response_login.cookies.get(cookie_key), "refresh_token не найден в куках"

    async def test_get_data_client(self, async_client: AsyncClient, get_user_token: dict[str, str]) -> None:
        """Получение данных и выход пользователя """
        response_authentic: Response = await async_client.get(url="/api/v1/auth/me", headers=get_user_token)
        assert response_authentic.status_code == 200, f"Ошибка получение данных пользователя: {response_authentic.text}"
        assert response_authentic.json()["id"] == 1 or 2
        assert response_authentic.json()["username"] == "Test"
        assert response_authentic.json()["email"] == "user2@example.com"

        response_logout: Response = await async_client.get(url="/api/v1/auth/logout", headers=get_user_token)
        assert response_logout.status_code == 200
