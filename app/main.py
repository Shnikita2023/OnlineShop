import sentry_sdk
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
from sqladmin import Admin
from starlette_exporter import handle_metrics, PrometheusMiddleware

from app.api_v1 import router as router_v1
from app.api_v1.admin_panel import admin_classes
from app.api_v1.admin_panel.auth import authentication_backend
from app.api_v1.middlewares.middleware import RateLimitMiddleware
from app.config import settings
from app.db.database import get_async_redis_client, engine

app = FastAPI(
    docs_url="/api/docs",
    debug=True,
    title="FastAPI OnlineShop"
)

admin = Admin(app=app,
              engine=engine,
              title="Админ панель",
              authentication_backend=authentication_backend)

app.include_router(router_v1, prefix="/api/v1")
app.add_route("/metrics", handle_metrics)

for classes in admin_classes:
    admin.add_view(classes)


@app.on_event("startup")
async def startup():
    async for redis_client in get_async_redis_client():
        FastAPICache.init(RedisBackend(redis_client), prefix="fastapi-cache")


app.add_middleware(RateLimitMiddleware)

app.add_middleware(PrometheusMiddleware)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS", "DELETE", "PATCH", "PUT"],
    allow_headers=["Content-Type", "Set-Cookie", "Access-Control-Allow-Headers", "Access-Control-Allow-Origin",
                   "Authorization"],
)

sentry_sdk.init(
    dsn=settings.sentry_dsn.SENTRY_DSN,
    traces_sample_rate=1.0,
    profiles_sample_rate=1.0,
)

if __name__ == "__main__":
    uvicorn.run(app=app, port=8000)
