from fastapi import FastAPI
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
from fastapi.middleware.cors import CORSMiddleware

from app.api_v1 import router as router_v1
from app.db.database import get_async_redis_client


async def startup() -> None:
    """Подключение редиса при старте"""
    async for redis_client in get_async_redis_client():
        FastAPICache.init(RedisBackend(redis_client), prefix="fastapi-cache")


app = FastAPI(on_startup=[startup])
app.include_router(router_v1, prefix="/api/v1")

app.add_middleware(
    CORSMiddleware,
    allow_origins="http://localhost:3000/",
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS", "DELETE", "PATCH", "PUT"],
    allow_headers=["Content-Type", "Set-Cookie", "Access-Control-Allow-Headers", "Access-Control-Allow-Origin",
                   "Authorization"],
)
