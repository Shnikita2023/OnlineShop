import secrets

from celery.result import AsyncResult
from redis.asyncio.client import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from app.api_v1.auth.password_service import password_service
from app.api_v1.exceptions import HttpAPIException
from app.api_v1.users.database import user_db
from app.api_v1.users.models import User
from app.api_v1.users.validators import UserValidator
from app.api_v1.utils.send_letter_on_email import send_password_reset_email


class PasswordForgot:
    """
    Класс для восстановления пароля пользователя
    """

    def __init__(self,
                 user_email: str,
                 session: AsyncSession,
                 redis_client: Redis):
        self.user_email = user_email
        self.session = session
        self.redis_client = redis_client

    async def forgot_password_user(self) -> dict:
        user: User | None = await UserValidator.validate_user_data_by_email(session=self.session,
                                                                            user_email=self.user_email)
        if user:
            token: str = await TokenGenerator.generate_temporary_token()
            await self.set_token_by_redis(user_id=user.id,
                                          token=token,
                                          redis_client=self.redis_client)
            result_task_send_email: AsyncResult = send_password_reset_email.delay(email=user.email, token=token)

            if result_task_send_email.ready():
                return {"message": "На ваш email отправлена ссылка на сброс пароля"}

            raise HttpAPIException(exception="Error run task by send message on email").http_error_500

        raise HttpAPIException(exception="check the correctness your email").http_error_400

    @staticmethod
    async def set_token_by_redis(user_id: int, token: str, redis_client: Redis):
        await redis_client.setex(name=f"user_{user_id}", value=token, time=6000)
        return token


class PasswordReset:
    """
    Класс для сброса пароля пользователя
    """

    def __init__(self,
                 user_email: str,
                 session: AsyncSession,
                 redis_client: Redis,
                 token: str,
                 password: str):
        self.user_email = user_email
        self.session = session
        self.redis_client = redis_client
        self.token = token
        self.password = password

    async def reset_password_user(self) -> dict:
        user_current: User = await user_db.get_user_by_email(session=self.session,
                                                             email=self.user_email)
        if user_current:
            await self.verify_token(token=self.token,
                                    redis_client=self.redis_client,
                                    user_id=user_current.id)
            new_password: bytes = password_service.hash_password(password=self.password)
            new_data: dict[str, bytes] = {'password': new_password}
            await user_db.update_partially_data_user(session=self.session,
                                                     id_data=user_current.id,
                                                     new_data=new_data)
            return {"message": "Пароль успешно сброшен и установлен новый"}

        raise HttpAPIException(exception="check the correctness your email").http_error_400

    @staticmethod
    async def verify_token(token: str,
                           redis_client: Redis,
                           user_id: int) -> bool:
        token_key: str = await redis_client.get(f"user_{user_id}")

        if token == token_key:
            return True

        raise HttpAPIException(exception="Token not found").http_error_400


class TokenGenerator:
    """
    Класс для генерации простого токена
    """

    @staticmethod
    async def generate_temporary_token() -> str:
        token: str = secrets.token_hex(32)
        return token
