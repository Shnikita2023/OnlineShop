import asyncio
from typing import AsyncGenerator, Any

import pytest
import redis.asyncio as redis
from fastapi.testclient import TestClient
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
from redis.asyncio.client import Redis
from redis.asyncio.connection import ConnectionPool
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, AsyncEngine, async_sessionmaker
from sqlalchemy.pool import NullPool

from app.api_v1.depends.dependencies import get_session
from app.api_v1.utils.unitofwork import UnitOfWork
from app.main import app
from app.config import settings
from app.db import Base, get_async_session, async_session_maker
from app.db.database import pool_redis, get_async_redis_client
from app.api_v1.auth.password_service import password_service
from app.api_v1.users.models import User

# DATABASE
DATABASE_URL_TEST: str = settings.db.database_test_url_asyncpg

engine_test: AsyncEngine = create_async_engine(DATABASE_URL_TEST, poolclass=NullPool)
async_session_maker_test: async_sessionmaker[AsyncSession] = async_sessionmaker(engine_test, class_=AsyncSession,
                                                                                expire_on_commit=False)
Base.metadata.bind = engine_test

pool_redis_test: ConnectionPool = redis.ConnectionPool.from_url(url=f"redis://{settings.redis.REDIS_HOST_TEST}:"
                                                                    f"{settings.redis.REDIS_PORT_TEST}",
                                                                encoding="utf8",
                                                                decode_responses=True)


async def get_async_redis_client_test() -> AsyncGenerator[Redis, Any]:
    async with redis.Redis(connection_pool=pool_redis_test) as redis_client:
        yield redis_client


async def get_async_session_test() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker_test() as session:
        yield session


async def get_session_test() -> UnitOfWork:
    """Получение экземпляра класса с тестовой сессии"""
    return UnitOfWork(session_factory=async_session_maker_test)

app.dependency_overrides[async_session_maker] = async_session_maker_test
app.dependency_overrides[get_async_session] = get_async_session_test
app.dependency_overrides[get_session] = get_session_test
app.dependency_overrides[pool_redis] = pool_redis_test
app.dependency_overrides[get_async_redis_client] = get_async_redis_client_test


@pytest.fixture(autouse=True, scope="session")
async def prepare_database():
    """Фикстура на создание и удаление таблицы"""
    async with engine_test.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine_test.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture(autouse=True, scope="session")
async def init_redis():
    """Инициализация редис для работы с кэшом и удалению данных"""
    async for redis_client in get_async_redis_client_test():
        FastAPICache.init(RedisBackend(redis_client), prefix="fastapi-cache")
    yield
    async for redis_client in get_async_redis_client_test():
        await redis_client.flushall()


@pytest.fixture(autouse=True, scope="session")
def event_loop(request):
    """Фикстура для создания экземпляра цикла событий"""
    loop: asyncio.AbstractEventLoop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


client: TestClient = TestClient(app)  # Создание синхронного клиента


@pytest.fixture(scope="session")
async def async_client() -> AsyncGenerator[AsyncClient, None]:
    """Фикстура для создания асинхронного клиента"""
    async with AsyncClient(app=app, base_url="http://test") as async_client:
        yield async_client


@pytest.fixture(scope="session")
async def async_redis_client() -> Redis:
    """Фикстура для получения асинхронного redis клиента"""
    async for redis_client in get_async_redis_client_test():
        return redis_client


async def register_and_login(async_client: AsyncClient,
                             username: str,
                             email: str,
                             password: str,
                             is_superuser: bool = False,
                             is_verified: bool = False) -> dict:
    """Получение куков после прохождение регистрации/аутентификации"""
    hashed_password = password_service.hash_password(password=password)
    async with async_session_maker_test() as session:
        user = User(username=username,
                    email=email,
                    password=hashed_password,
                    is_superuser=is_superuser,
                    is_verified=is_verified)
        session.add(user)
        await session.commit()

    login_data = {
        "email": email,
        "password": password
    }

    response_login = await async_client.post("/api/v1/auth/login", data=login_data)
    assert response_login.status_code == 200, f"Ошибка авторизации: {response_login.text}"

    cookie_user = list(response_login.cookies.values())[0]
    return {"Cookie": f"{settings.session_cookie.COOKIE_SESSION_KEY}={cookie_user}"}


@pytest.fixture(scope="session")
async def get_cookie_user(async_client: AsyncClient) -> dict:
    """Фикстура для получения куков с токеном авторизованного клиента"""
    username = "Test"
    email = "test@example.com"
    password = "string1fadH!"

    return await register_and_login(async_client=async_client,
                                    username=username,
                                    email=email,
                                    password=password)


@pytest.fixture(scope='session')
async def get_cookie_is_superuser(async_client: AsyncClient) -> dict:
    """Фикстура для получения куков с токеном клиента superuser"""
    username = "Admin"
    email = "admin@mail.ru"
    password = "Qwerty!1"
    is_superuser = True
    is_verified = True

    return await register_and_login(async_client=async_client,
                                    username=username,
                                    email=email,
                                    password=password,
                                    is_superuser=is_superuser,
                                    is_verified=is_verified)
