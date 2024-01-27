from pathlib import Path

from pydantic import BaseModel
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).parent.parent


class Base(BaseSettings):
    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8')


class DbSettings(Base):
    DB_HOST: str
    DB_PORT: int
    DB_NAME: str
    DB_USER: str
    DB_PASS: str

    DB_HOST_TEST: str
    DB_PORT_TEST: int
    DB_NAME_TEST: str
    DB_PASS_TEST: str
    DB_USER_TEST: str

    POSTGRES_PASSWORD: str
    POSTGRES_USER: str
    POSTGRES_DB: str

    @property
    def database_url_asyncpg(self) -> str:
        return (f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASS}@"
                f"{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}")

    @property
    def database_test_url_asyncpg(self) -> str:
        return (f"postgresql+asyncpg://{self.DB_USER_TEST}:{self.DB_PASS_TEST}@"
                f"{self.DB_HOST_TEST}:{self.DB_PORT_TEST}/{self.DB_NAME_TEST}")


class EmailSettings(Base):
    SMTP_PASSWORD: str
    SMTP_USER: str
    SMTP_HOST: str
    SMTP_PORT: int


class RedisSettings(Base):
    REDIS_HOST: str
    REDIS_PORT: int


class SessionCookie(Base):
    COOKIE_SESSION_KEY: str
    COOKIE_SESSION_TIME: int


class AuthJWT(BaseModel):
    private_key: Path = BASE_DIR / "certs" / "jwt-private.pem"
    public_key: Path = BASE_DIR / "certs" / "jwt-public.pem"
    algorithm: str = "RS256"
    access_token_expire_minute: int = 60000


class Settings(BaseModel):
    db: DbSettings = DbSettings()
    auth_jwt: AuthJWT = AuthJWT()
    email: EmailSettings = EmailSettings()
    redis: RedisSettings = RedisSettings()
    session_cookie: SessionCookie = SessionCookie()


settings = Settings()
