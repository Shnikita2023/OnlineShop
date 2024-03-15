import pytest
from httpx import Response, AsyncClient
from redis.asyncio.client import Redis

from app.config import settings


class TestUserManagement:
    """
    Класс для работы с пользователем
    """

    user_register_data = {
        "username": "User",
        "password": "string1fadH!",
        "email": "user@example.com",
    }

    user_login_data = {
        "email": "user@example.com",
        "password": "string1fadH!",
    }

    @pytest.mark.parametrize(
        "expected_status, expected_details, error_details",
        [
            (201, None, None),
            (400, "Данный пользователь уже зарегистрирован, выберите другой email.", "error")
        ]
    )
    async def test_register_client(self,
                                   async_client: AsyncClient,
                                   expected_status: int,
                                   expected_details: str | None,
                                   error_details: str | None) -> None:
        """Регистрация пользователя"""
        response_register: Response = await async_client.post(url="/api/v1/auth/register", json=self.user_register_data)
        response_register_json = response_register.json()

        if expected_status == 201:
            assert response_register.status_code == expected_status
            assert response_register_json["id"] == 1
            assert response_register_json["username"] == "User"
            assert response_register_json["email"] == "user@example.com"

        else:
            assert response_register.status_code == expected_status
            assert response_register_json["detail"]["status"] == error_details
            assert response_register_json["detail"]["details"] == expected_details

    async def test_login_client(self, async_client: AsyncClient) -> None:
        """Аутентификация пользователя"""
        response_login: Response = await async_client.post(url="/api/v1/auth/login", data=self.user_login_data)
        cookie_key = settings.session_cookie.COOKIE_SESSION_KEY
        assert response_login.status_code == 200, f"Ошибка авторизации: {response_login.text}"
        assert cookie_key in response_login.cookies, f"не существует ключа {cookie_key} в куках"
        assert "access_token" in response_login.cookies.get(cookie_key), "access_token не найден в куках"
        assert "refresh_token" in response_login.cookies.get(cookie_key), "refresh_token не найден в куках"

    async def test_get_data_and_logout_client(self, async_client: AsyncClient, get_cookie_user: dict[str, str]) -> None:
        """Получение данных и выход пользователя """
        response_authentic: Response = await async_client.get(url="/api/v1/auth/me", headers=get_cookie_user)
        assert response_authentic.status_code == 200, f"Ошибка получение данных пользователя: {response_authentic.text}"
        assert response_authentic.json()["id"] == 1 or 2
        assert response_authentic.json()["username"] == "Test"
        assert response_authentic.json()["email"] == "test@example.com"

        response_logout: Response = await async_client.get(url="/api/v1/auth/logout", headers=get_cookie_user)
        assert response_logout.status_code == 200
        assert response_logout.json() == {"message": "logout successful"}

    async def test_forgot_password(self, async_client: AsyncClient) -> None:
        """Восстановление пароля пользователя"""
        response_forgot: Response = await async_client.post(url="/api/v1/auth/forgot_password",
                                                            json={
                                                                "email": "user@example.com"
                                                            })
        assert response_forgot.status_code == 200
        assert response_forgot.json() == {"message": "На ваш email отправлена ссылка на сброс пароля"}

    async def test_reset_password(self, async_client: AsyncClient, async_redis_client: Redis) -> None:
        """Сброс пароля пользователя"""
        token_client = await async_redis_client.get("user_1")
        reset_data = {"email": "user@example.com", "token": token_client, "password": "Levo!567x"}
        response_reset: Response = await async_client.post(url="/api/v1/auth/reset_password",
                                                           json=reset_data)
        assert response_reset.status_code == 200
        assert response_reset.json() == {"message": "Пароль успешно сброшен и установлен новый"}
