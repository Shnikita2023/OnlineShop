import re
from typing import Optional

from fastapi import HTTPException
from pydantic import BaseModel, EmailStr, ConfigDict, field_validator
from starlette import status

from app.logging_config import MyLogger
from .constants import (FAILED_ERROR_LOGIN, PASSWORD_LENGTH_ERROR, STATUS_CODE_400,
                        PASSWORD_UPPERCASE_ERROR, PASSWORD_LOWERCASE_ERROR, PASSWORD_DIGIT_ERROR,
                        USERNAME_ERROR, IS_SUPERUSER_ERROR, IS_VERIFIED_ERROR, PASSWORD_SPECIAL_CHAR_ERROR)

logger = MyLogger(pathname=__name__).init


class UserCreate(BaseModel):
    username: str
    password: str
    email: EmailStr
    is_active: Optional[bool] = True
    is_superuser: Optional[bool] = False
    is_verified: Optional[bool] = False

    @field_validator("password")
    def check_password(cls, password: str) -> str:
        PATTERN_PASSWORD = r"[!@#$%^&*()\-_=+{};:,<.>|\[\]\\/?]"
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
        if not re.search(PATTERN_PASSWORD, password):
            logger.info(f"{FAILED_ERROR_LOGIN}\n{PASSWORD_SPECIAL_CHAR_ERROR}{STATUS_CODE_400}")
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                detail=PASSWORD_SPECIAL_CHAR_ERROR)

        return password

    @field_validator("username")
    def check_username(cls, username):
        PATTERN_USERNAME = r"^[А-ЯЁ][а-яё]+$|^[A-Z][a-z]+$"

        if not re.match(PATTERN_USERNAME, username):
            logger.info(f"{FAILED_ERROR_LOGIN}\n{USERNAME_ERROR}{STATUS_CODE_400}")
            raise HTTPException(status_code=400,
                                detail=USERNAME_ERROR)

        return username

    @field_validator("is_superuser")
    def check_superuser(cls, is_superuser):

        if is_superuser is True:
            logger.info(f"{FAILED_ERROR_LOGIN}\n{IS_SUPERUSER_ERROR}{STATUS_CODE_400}")
            raise HTTPException(status_code=400, detail=IS_SUPERUSER_ERROR)

        return is_superuser

    @field_validator("is_verified")
    def check_verified(cls, is_verified):

        if is_verified is True:
            logger.info(f"{FAILED_ERROR_LOGIN}\n{IS_VERIFIED_ERROR}{STATUS_CODE_400}")
            raise HTTPException(status_code=400, detail=IS_VERIFIED_ERROR)

        return is_verified


class UserShow(BaseModel):
    model_config = ConfigDict(strict=True)

    id: int
    username: str
    email: EmailStr


class UserUpdate(UserCreate):
    pass


class ForgotUser(BaseModel):
    email: EmailStr


class ResetUser(BaseModel):
    password: str
    token: str
    email: EmailStr

    @field_validator("password")
    def check_password(cls, password: str) -> str:
        return UserCreate.check_password(password=password)
