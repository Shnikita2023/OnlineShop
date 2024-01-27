import asyncio
import pytest
from asyncio import AbstractEventLoop
from typing import AsyncGenerator
from fastapi.testclient import TestClient
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, AsyncEngine, async_sessionmaker
from sqlalchemy.pool import NullPool

from app.config import settings
from app.db import Base, get_async_session, async_session_maker
from app.main import app

# DATABASE
DATABASE_URL_TEST: str = settings.db.database_test_url_asyncpg

engine_test: AsyncEngine = create_async_engine(DATABASE_URL_TEST, poolclass=NullPool)
async_session_maker_test: async_sessionmaker[AsyncSession] = async_sessionmaker(engine_test, class_=AsyncSession,
                                                                                expire_on_commit=False)
Base.metadata.bind = engine_test


async def get_async_session_test() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker_test() as session:
        yield session


app.dependency_overrides[async_session_maker] = async_session_maker_test
app.dependency_overrides[get_async_session] = get_async_session_test


@pytest.fixture(autouse=True, scope='session')
async def prepare_database():
    """Фикстура на создание и удаление таблицы"""
    async with engine_test.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine_test.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture(scope='session')
def event_loop(request):
    """Фикстура для создание экземпляра цикла событий по умолчанию для каждого тестового примера"""
    loop: AbstractEventLoop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


client: TestClient = TestClient(app)


@pytest.fixture(scope="session")
async def async_client() -> AsyncGenerator[AsyncClient, None]:
    """Фикстура для создание асинхронного клиента"""
    async with AsyncClient(app=app, base_url="http://test") as async_client:
        yield async_client

#
# @pytest.fixture(scope="session")
# def get_user_token() -> dict:
#     """Фикстура для получение токена авторизованного клиента"""
#     data: dict[str, Any] = {
#         "email": "usertest@mail.ru",
#         "password": "test35H!ss",
#         "is_active": True,
#         "is_superuser": False,
#         "is_verified": False,
#         "username": "ivan",
#         "last_name": "Ivanov",
#         "first_name": "Irina"
#     }
#     response: Response = client.post("/auth/register", json=data)
#     assert response.status_code == 201, f"Ошибка при создании пользователя: {response.text}"
#
#     data: dict[str, str] = {
#         "username": "usertest@mail.ru",
#         "password": "test35H!ss",
#     }
#     response: Response = client.post("/auth/jwt/login", data=data)
#     assert response.status_code == 200 or 204, f"Ошибка авторизации: {response.text}"
#
#     cookie: str = response.headers["set-cookie"].split(";")[0]
#     return {"Cookie": cookie}
