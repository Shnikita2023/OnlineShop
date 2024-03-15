import os
from pathlib import Path

from pydantic_settings import BaseSettings
from dotenv import load_dotenv

BASE_DIR = Path(__file__).parent.parent

load_dotenv(BASE_DIR / ".env.dev")


class DbSettings(BaseSettings):
    DB_HOST: str = os.getenv("DB_HOST")
    DB_PORT: int = os.getenv("DB_PORT")
    DB_NAME: str = os.getenv("DB_NAME")
    DB_USER: str = os.getenv("DB_USER")
    DB_PASS: str = os.getenv("DB_PASS")

    DB_HOST_TEST: str = os.getenv("DB_HOST_TEST")
    DB_PORT_TEST: int = os.getenv("DB_PORT_TEST")
    DB_NAME_TEST: str = os.getenv("DB_NAME_TEST")
    DB_PASS_TEST: str = os.getenv("DB_PASS_TEST")
    DB_USER_TEST: str = os.getenv("DB_USER_TEST")

    POSTGRES_PASSWORD: str = os.getenv("POSTGRES_PASSWORD")
    POSTGRES_USER: str = os.getenv("POSTGRES_USER")
    POSTGRES_DB: str = os.getenv("POSTGRES_DB")

    @property
    def database_url_asyncpg(self) -> str:
        return (f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASS}@"
                f"{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}")

    @property
    def database_test_url_asyncpg(self) -> str:
        return (f"postgresql+asyncpg://{self.DB_USER_TEST}:{self.DB_PASS_TEST}@"
                f"{self.DB_HOST_TEST}:{self.DB_PORT_TEST}/{self.DB_NAME_TEST}")


class EmailSettings(BaseSettings):
    SMTP_PASSWORD: str = os.getenv("SMTP_PASSWORD")
    SMTP_USER: str = os.getenv("SMTP_USER")
    SMTP_HOST: str = os.getenv("SMTP_HOST")
    SMTP_PORT: int = os.getenv("SMTP_PORT")


class RedisSettings(BaseSettings):
    REDIS_HOST: str = os.getenv("REDIS_HOST")
    REDIS_PORT: int = os.getenv("REDIS_PORT")

    REDIS_HOST_TEST: str = os.getenv("REDIS_HOST_TEST")
    REDIS_PORT_TEST: int = os.getenv("REDIS_PORT_TEST")


class CelerySettings(BaseSettings):
    CELERY_BROKER_URL: str = os.getenv("CELERY_BROKER_URL")
    CELERY_RESULT_BACKEND: str = os.getenv("CELERY_RESULT_BACKEND")


class SessionCookie(BaseSettings):
    COOKIE_SESSION_KEY: str = os.getenv("COOKIE_SESSION_KEY")
    COOKIE_SESSION_TIME: int = os.getenv("COOKIE_SESSION_TIME")


class SentryAPI(BaseSettings):
    SENTRY_DSN: str = os.getenv("SENTRY_DSN")


class AuthJWT(BaseSettings):
    PRIVATE_KEY: Path = BASE_DIR / "certs" / "jwt-private.pem"
    PUBLIC_KEY: Path = BASE_DIR / "certs" / "jwt-public.pem"
    ALGORITHM: str = "RS256"
    ACCESS_TOKEN_EXPIRE_MINUTE: int = os.getenv("ACCESS_TOKEN_EXPIRE_MINUTE")
    REFRESH_TOKEN_EXPIRE_MINUTE: int = os.getenv("REFRESH_TOKEN_EXPIRE_MINUTE")


class Settings:
    db: DbSettings = DbSettings()
    auth_jwt: AuthJWT = AuthJWT()
    email: EmailSettings = EmailSettings()
    redis: RedisSettings = RedisSettings()
    session_cookie: SessionCookie = SessionCookie()
    sentry_dsn: SentryAPI = SentryAPI()
    celery: CelerySettings = CelerySettings()


settings = Settings()
