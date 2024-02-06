import pytest
from httpx import Response, AsyncClient

from app.config import settings


@pytest.fixture(scope="session")
async def get_user_token(async_client: AsyncClient) -> dict:
    """Фикстура для получения токена авторизованного клиента"""

    data_registration: dict[str, str] = {
        "password": "string1fadH!",
        "email": "user2@example.com",
        "username": "Test",
    }
    response_register: Response = await async_client.post("/api/v1/auth/register", json=data_registration)
    assert response_register.status_code == 201, f"Ошибка при создании пользователя: {response_register.text}"

    data_auth: dict[str, str] = {
        "email": "user2@example.com",
        "password": "string1fadH!",
    }
    response_login: Response = await async_client.post("/api/v1/auth/login", data=data_auth)
    assert response_login.status_code == 200, f"Ошибка авторизации: {response_login.text}"

    cookie_user: str = list(response_login.cookies.values())[0]
    return {"Cookie": f"{settings.session_cookie.COOKIE_SESSION_KEY}={cookie_user}"}
