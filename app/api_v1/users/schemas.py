import re
from typing import Optional

from fastapi import HTTPException
from pydantic import BaseModel, ConfigDict, field_validator, Field
from starlette import status

from app.logging_config import MyLogger
from .constants import (FAILED_ERROR_LOGIN, PASSWORD_LENGTH_ERROR, STATUS_CODE_400, EMAIL_ERROR,
                        PASSWORD_UPPERCASE_ERROR, PASSWORD_LOWERCASE_ERROR, PASSWORD_DIGIT_ERROR,
                        USERNAME_ERROR, IS_SUPERUSER_ERROR, IS_VERIFIED_ERROR, PASSWORD_SPECIAL_CHAR_ERROR)

logger = MyLogger(pathname=__name__).init_logger


class EmailUser(BaseModel):
    email: str = Field(default="user@mail.ru")

    @field_validator("email")
    def validate_email(cls, email):
        EMAIL_REGEX = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
        # Проверка формата email
        if not re.match(EMAIL_REGEX, email):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                detail=EMAIL_ERROR)
        return email


class PasswordUser(BaseModel):
    password: str

    @field_validator("password")
    def validate_password(cls, password: str) -> str:
        PASSWORD_REGEX = r"[!@#$%^&*()\-_=+{};:,<.>|\[\]\\/?]"
        # Проверка на длину пароля
        if len(password) < 8 or len(password) > 50:
            logger.info(f"{FAILED_ERROR_LOGIN}\n{PASSWORD_LENGTH_ERROR}{STATUS_CODE_400}")
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                detail=PASSWORD_LENGTH_ERROR)

        # Проверка на наличие хотя бы одной заглавной буквы
        if not any(c.isupper() for c in password):
            logger.info(f"{FAILED_ERROR_LOGIN}\n{PASSWORD_UPPERCASE_ERROR}{STATUS_CODE_400}")
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                detail=PASSWORD_UPPERCASE_ERROR)

        # Проверка на наличие хотя бы одной строчной буквы
        if not any(c.islower() for c in password):
            logger.info(f"{FAILED_ERROR_LOGIN}\n{PASSWORD_LOWERCASE_ERROR}{STATUS_CODE_400}")
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                detail=PASSWORD_LOWERCASE_ERROR)

        # Проверка на наличие хотя бы одной цифры
        if not any(c.isdigit() for c in password):
            logger.info(f"{FAILED_ERROR_LOGIN}\n{PASSWORD_DIGIT_ERROR}{STATUS_CODE_400}")
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                detail=PASSWORD_DIGIT_ERROR)

        # Проверка на наличие хотя бы одного специального символа
        if not re.search(PASSWORD_REGEX, password):
            logger.info(f"{FAILED_ERROR_LOGIN}\n{PASSWORD_SPECIAL_CHAR_ERROR}{STATUS_CODE_400}")
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                detail=PASSWORD_SPECIAL_CHAR_ERROR)

        return password


class UserCreate(EmailUser, PasswordUser):
    username: str
    is_active: Optional[bool] = True
    is_superuser: Optional[bool] = False
    is_verified: Optional[bool] = False

    @field_validator("username")
    def validate_username(cls, username):
        USERNAME_REGEX = r"^[А-ЯЁ][а-яё]+$|^[A-Z][a-z]+$"

        if not re.match(USERNAME_REGEX, username):
            logger.info(f"{FAILED_ERROR_LOGIN}\n{USERNAME_ERROR}{STATUS_CODE_400}")
            raise HTTPException(status_code=400,
                                detail=USERNAME_ERROR)
        return username

    @field_validator("is_superuser")
    def validate_superuser(cls, is_superuser):

        if is_superuser is True:
            logger.info(f"{FAILED_ERROR_LOGIN}\n{IS_SUPERUSER_ERROR}{STATUS_CODE_400}")
            raise HTTPException(status_code=400, detail=IS_SUPERUSER_ERROR)

        return is_superuser

    @field_validator("is_verified")
    def validate_verified(cls, is_verified):

        if is_verified is True:
            logger.info(f"{FAILED_ERROR_LOGIN}\n{IS_VERIFIED_ERROR}{STATUS_CODE_400}")
            raise HTTPException(status_code=400, detail=IS_VERIFIED_ERROR)

        return is_verified


class UserShow(EmailUser):
    model_config = ConfigDict(strict=True)

    id: int
    username: str


class UserUpdate(UserCreate):
    pass


class ForgotUser(EmailUser):
    pass


class ResetUser(EmailUser, PasswordUser):
    token: str
