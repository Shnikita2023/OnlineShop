import pytest
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


client: TestClient = TestClient(app)


@pytest.fixture(scope="session")
async def async_client() -> AsyncGenerator[AsyncClient, None]:
    """Фикстура для создание асинхронного клиента"""
    async with AsyncClient(app=app, base_url="http://test") as async_client:
        yield async_client
