from datetime import datetime, timedelta

import jwt
from fastapi import Depends, Response

from app.api_v1.auth.cookie_token_service import cookie_helper
from app.api_v1.exceptions import HttpAPIException
from app.api_v1.users.schemas import UserCreate
from app.config import settings


class TokenService:
    """
    Класс для кодирования/декодирование jwt токена
    """

    ACCESS_TOKEN_EXPIRE_MINUTE: int = settings.auth_jwt.ACCESS_TOKEN_EXPIRE_MINUTE
    REFRESH_TOKEN_EXPIRE_MINUTE: int = settings.auth_jwt.REFRESH_TOKEN_EXPIRE_MINUTE
    PRIVATE_KEY: str = settings.auth_jwt.PRIVATE_KEY.read_text()
    PUBLIC_KEY: str = settings.auth_jwt.PUBLIC_KEY.read_text()
    ALGORITHM: str = settings.auth_jwt.ALGORITHM

    @classmethod
    def encode_jwt(cls, payload: dict) -> str:

        if len(payload) > 1:
            expire_minutes = cls.ACCESS_TOKEN_EXPIRE_MINUTE
        else:
            expire_minutes = cls.REFRESH_TOKEN_EXPIRE_MINUTE

        to_encode: dict = payload.copy()
        now_time: datetime = datetime.utcnow()
        expire_token: datetime = now_time + timedelta(minutes=expire_minutes)
        to_encode.update(exp=expire_token, iat=now_time)
        encoded: str = jwt.encode(payload=to_encode, key=cls.PRIVATE_KEY, algorithm=cls.ALGORITHM)
        return encoded

    @classmethod
    def decode_jwt(cls, token: bytes | str) -> dict:
        try:
            decoded: dict = jwt.decode(jwt=token, key=cls.PUBLIC_KEY, algorithms=[cls.ALGORITHM])

        except jwt.ExpiredSignatureError:
            decoded: dict = jwt.decode(jwt=token,
                                       key=cls.PUBLIC_KEY,
                                       algorithms=[cls.ALGORITHM],
                                       options={"verify_exp": False})
        return decoded


class TokenWork(TokenService):
    """Класс для работы с токенами пользователей"""

    @classmethod
    def create_tokens(cls, user: UserCreate, response: Response) -> tuple:
        access_jwt_payload = {
            "sub": user.id,
            "username": user.username,
            "email": user.email,
            "is_superuser": user.is_superuser
        }
        refresh_jwt_payload = {"sub": user.id}
        access_token = cls.encode_jwt(payload=access_jwt_payload)
        refresh_token = cls.encode_jwt(payload=refresh_jwt_payload)
        cookie_helper.create_cookie_for_tokens(response, access_token, refresh_token)
        return access_token, refresh_token

    @classmethod
    def create_new_access_token(cls, access_token_payload: dict) -> str:
        new_access_token = cls.encode_jwt(payload=access_token_payload)
        return new_access_token

    @classmethod
    def check_expires_tokens(cls,
                             access_token_payload: dict,
                             refresh_token_payload: dict) -> str | None:
        expire_access_token = datetime.fromtimestamp(access_token_payload["exp"])
        expire_refresh_token = datetime.fromtimestamp(refresh_token_payload["exp"])

        if expire_access_token <= datetime.now() and expire_refresh_token <= datetime.now():
            raise HttpAPIException(exception="invalid token").http_error_401

        if expire_access_token <= datetime.now():
            return cls.create_new_access_token(access_token_payload)

        return None

    @classmethod
    def get_current_token_payload(cls,
                                  response: Response,
                                  cookie_tokens: str = Depends(cookie_helper.get_cookie_tokens)) -> dict:
        try:
            access_token, refresh_token = cookie_helper.parsing_cookie_tokens(cookie_tokens)
            access_token_payload: dict = cls.decode_jwt(token=access_token)
            refresh_token_payload: dict = cls.decode_jwt(token=refresh_token)
            new_token: str | None = cls.check_expires_tokens(access_token_payload, refresh_token_payload)

            if new_token:
                cookie_helper.create_cookie_for_tokens(response, new_token, refresh_token)

            return access_token_payload

        except jwt.InvalidTokenError:
            raise HttpAPIException(exception="invalid token").http_error_401
