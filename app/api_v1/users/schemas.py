import re
from typing import Optional

from fastapi import HTTPException
from pydantic import BaseModel, EmailStr, ConfigDict, field_validator
from starlette import status

from app.logging_config import MyLogger

logger = MyLogger(pathname=__name__).init
PATTERN = r"^[А-ЯЁ][а-яё]+$|^[A-Z][a-z]+$"


class UserCreate(BaseModel):
    username: str
    password: str
    email: EmailStr
    is_active: Optional[bool] = True
    is_superuser: Optional[bool] = False
    is_verified: Optional[bool] = False

    @field_validator("password")
    def check_password(cls, password: str) -> str:
        # Проверка на длину пароля
        if len(password) < 8 or len(password) > 50:
            logger.info("Неудачная попытка входа. "
                        "Пароль не соответствует требованиям.\n"
                        "Длина пароля должна быть не менее 8 символов. Status: 400")
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                detail="Пароль должен быть от 8 до 50 символов")

        # Проверка на наличие хотя бы одной заглавной буквы
        if not any(c.isupper() for c in password):
            logger.info("Неудачная попытка входа.\n"
                        "В пароли должна быть хотя бы одна заглавная буква. Status: 400")
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                detail="В пароли должна быть хотя бы одна заглавная буква")

        # Проверка на наличие хотя бы одной строчной буквы
        if not any(c.islower() for c in password):
            logger.info("Неудачная попытка входа.\n"
                        "В пароли должна быть хотя бы одна строчная буква. Status: 400")
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                detail="В пароли должна быть хотя бы одна строчная буква")

        # Проверка на наличие хотя бы одной цифры
        if not any(c.isdigit() for c in password):
            logger.info("Неудачная попытка входа.\n"
                        "В пароли должна быть хотя бы одна цифра. Status: 400")
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                detail="В пароли должна быть хотя бы одна цифра")

        # Проверка на наличие хотя бы одного специального символа
        if not re.search(r'[!@#$%^&*()\-_=+{};:,<.>|\[\]\\/?]', password):
            logger.info("Неудачная попытка входа.\n"
                        "В пароли должен быть хотя бы один символ: !@#$%^&{}()\[]-_=+;:,<.>|/?. Status: 400")
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                detail="В пароли должен быть хотя бы один символ: !!@#$%^&{}()\[]-_=+;:,<.>|/?")

        return password

    @field_validator("username")
    def check_username(cls, username):
        if not username.isalpha():
            logger.info("Неудачная попытка входа.\n"
                        "Поля 'username' должен содержать только буквы Status: 400")
            raise HTTPException(status_code=400, detail="Поля 'username' должен содержать только буквы")
        return username

    @field_validator("is_superuser")
    def check_superuser(cls, is_superuser):
        if is_superuser is True:
            logger.info("Неудачная попытка входа.\n"
                        "Поля 'is_superuser' должен быть пустым или False Status: 400")
            raise HTTPException(status_code=400, detail="field 'is_superuser' must be False or Absent")
        return is_superuser

    @field_validator("is_verified")
    def check_verified(cls, is_verified):
        if is_verified is True:
            logger.info("Неудачная попытка входа.\n"
                        "Поля 'is_verified' должен быть пустым или False Status: 400")
            raise HTTPException(status_code=400, detail="field 'is_verified' must be False or Absent")
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


