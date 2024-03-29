from fastapi import Depends, Form, Response
from pydantic import EmailStr
from sqlalchemy.ext.asyncio import AsyncSession

from app.api_v1.auth.token_jwt_service import TokenWork
from app.api_v1.auth.password_service import password_service
from app.api_v1.users.validators import UserValidator
from app.api_v1.exceptions import HttpAPIException
from app.api_v1.users.models import User
from app.db import get_async_session
from app.logging_config import MyLogger

logger = MyLogger(pathname=__name__).init_logger


class AuthUser:
    """
    Класс для валидация пользователя
    """

    @staticmethod
    async def validate_auth_user(session: AsyncSession = Depends(get_async_session),
                                 email: EmailStr = Form(),
                                 password: str = Form()) -> User:
        user: User | None = await UserValidator.validate_user_data_by_field(session=session,
                                                                            field="email",
                                                                            value=email)

        if not user or email != user.email or not password_service.check_password(password=password,
                                                                                  hashed_password=user.password):
            raise HttpAPIException(exception="invalid username or password").http_error_401

        logger.info(f"Успешно пройдена валидация пользователя '{user.username}'. Status: 200")
        return user

    @staticmethod
    async def get_current_auth_user(response: Response,
                                    payload: dict = Depends(TokenWork.get_current_token_payload),
                                    session: AsyncSession = Depends(get_async_session)) -> dict:
        user_id: int = payload.get("sub")
        user: User | None = await UserValidator.validate_user_data_by_field(session=session,
                                                                            value=user_id)
        if user_id == user.id:
            logger.info(f"Получение данных о пользователе '{user.username}'. Status: 200")
            return payload

        raise HttpAPIException(exception="user not found").http_error_401
