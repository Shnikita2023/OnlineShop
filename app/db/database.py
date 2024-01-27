from typing import AsyncGenerator, Any

import redis.asyncio as redis
from redis.asyncio.client import Redis
from redis.asyncio.connection import ConnectionPool
from sqlalchemy.ext.asyncio import (create_async_engine, async_sessionmaker,
                                    AsyncSession, AsyncEngine)
from sqlalchemy.orm import Mapped, DeclarativeBase, mapped_column

from app.config import settings


class Base(DeclarativeBase):
    __abstract__ = True

    id: Mapped[int] = mapped_column(primary_key=True, index=True, autoincrement=True)


DATABASE_URL: str = settings.db.database_url_asyncpg

engine: AsyncEngine = create_async_engine(DATABASE_URL)
async_session_maker: async_sessionmaker[AsyncSession] = async_sessionmaker(engine,
                                                                           class_=AsyncSession,
                                                                           expire_on_commit=False)

pool_redis: ConnectionPool = redis.ConnectionPool.from_url(url=f"redis://localhost:6000",
                                                           encoding="utf8",
                                                           decode_responses=True)


async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        yield session


async def get_async_redis_client() -> AsyncGenerator[Redis, Any]:
    async with redis.Redis(connection_pool=pool_redis) as redis_client:
        yield redis_client
